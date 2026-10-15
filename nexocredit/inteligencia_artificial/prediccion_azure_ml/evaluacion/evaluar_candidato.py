"""Evaluate the verified Azure artifact offline, without fitting or threshold tuning.

Run ONLY in an isolated container with trusted model input, no network, no secrets,
read-only data mounts and a dedicated output folder. Pickle can execute code.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import signal
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_ZIP = "649b9c1489bcdb2e826cdf6fa4dd809db5d6a369600c6b4b8a442a25896ee9ee"
EXPECTED_MODEL = "b7d18b9419c7a1184f07a01c7a774f291d795d7d679eaa46e7a4db9325e84f58"
HASHES = {
    "train": "d3f2caae94533112d2c0a58241fdb9e1641d6d2ad9cef10635c727ccde6f5b79",
    "validation": "212b599be2da5989d2762d2b7bc7516bfbb8f56990d988b6f80a7afd49684891",
    "test": "d7cf431db3eb63400d72a5cfca20d679396013ccc18ff5c902ff71215b01fb72",
}
FEATURES = ["LIMIT_BAL", "PAY_0", *[f"PAY_{i}" for i in range(2, 7)],
            *[f"BILL_AMT{i}" for i in range(1, 7)], *[f"PAY_AMT{i}" for i in range(1, 7)]]
TARGET = "incumplimiento_mes_siguiente"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    signal.alarm(600)  # Linux-only runner: hard stop instead of an unattended job.
    parser = argparse.ArgumentParser()
    for name in ("zip", "train", "validation", "test", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    require(sha(args.zip) == EXPECTED_ZIP, "Unexpected ZIP hash; do not load")
    require(not args.output.exists(), "Output exists; preserve previous evidence")
    import numpy as np
    import pandas as pd
    import yaml
    import mlflow.pyfunc
    import mlflow.sklearn
    from sklearn.metrics import (accuracy_score, average_precision_score,
                                 balanced_accuracy_score, brier_score_loss,
                                 confusion_matrix, f1_score, log_loss,
                                 precision_score, recall_score, roc_auc_score)

    data = {}
    for name, count in (("train", 17909), ("validation", 6136), ("test", 5955)):
        path = getattr(args, name)
        require(sha(path) == HASHES[name], f"{name}: data changed")
        frame = pd.read_csv(path)
        require(list(frame.columns) == FEATURES + [TARGET], f"{name}: column mismatch")
        require(len(frame) == count, f"{name}: row mismatch")
        require(not frame.isna().any().any(), f"{name}: missing values")
        require(set(frame[TARGET].unique()) == {0, 1}, f"{name}: invalid target")
        require(all(pd.api.types.is_integer_dtype(frame[c]) for c in FEATURES),
                f"{name}: noninteger feature")
        data[name] = frame
    groups = {name: set(map(tuple, frame[FEATURES].to_numpy())) for name, frame in data.items()}
    for left, right in (("train", "validation"), ("train", "test"), ("validation", "test")):
        require(not groups[left].intersection(groups[right]), f"Predictor overlap {left}/{right}")

    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model": "plurione-uci-voting-candidato:1",
        "source_run": "uci-incumplimiento-automl-1_4",
        "zip_sha256": EXPECTED_ZIP, "model_sha256": EXPECTED_MODEL,
        "data_sha256": HASHES, "predictor_overlap": 0,
        "python": platform.python_version(),
        "versions": {p: importlib.metadata.version(p) for p in
                     ("mlflow-skinny", "scikit-learn", "numpy", "pandas", "azureml-automl-runtime")},
        "method": "Frozen artifact; native predict and predict_proba; no fit or threshold search. Validation reproduction before independent test.",
        "limitations": ["Academic UCI data, Taiwan 2005; not representative of PluriOne applicants.",
                        "Grouped random split, not a temporal evaluation.",
                        "No production approval or integration with current app inputs.",
                        "No fairness or prospective calibration validation."],
    }
    with tempfile.TemporaryDirectory(prefix="plurione-model-") as folder:
        model_dir = Path(folder)
        with zipfile.ZipFile(args.zip) as archive:
            expected = {"MLmodel", "model.pkl", "conda.yaml", "requirements.txt", "python_env.yaml"}
            require(len(archive.infolist()) == 5 and set(archive.namelist()) == expected,
                    "Unexpected archive entries")
            require(archive.testzip() is None, "ZIP CRC failure")
            for entry in archive.infolist():
                require(entry.file_size < 2_000_000, "Oversized archive entry")
                (model_dir / entry.filename).write_bytes(archive.read(entry))
        require(sha(model_dir / "model.pkl") == EXPECTED_MODEL, "Wrong model bytes")
        meta = yaml.safe_load((model_dir / "MLmodel").read_text())
        require(meta["run_id"] == report["source_run"], "Wrong source run")
        require([c["name"] for c in json.loads(meta["signature"]["inputs"])] == FEATURES,
                "Model signature mismatch")
        print("Inputs and archive verified. Loading trusted model offline...", flush=True)
        model = mlflow.sklearn.load_model(str(model_dir))
        classes = np.asarray(model.classes_)
        require(classes.shape == (2,) and set(classes.tolist()) == {False, True},
                f"Unexpected class mapping: {classes}")
        positive_index = int(np.flatnonzero(classes == True)[0])
        pyfunc = mlflow.pyfunc.load_model(str(model_dir))
        smoke = data["validation"][FEATURES].iloc[:5]
        require(np.array_equal(pyfunc.predict(smoke), model.predict(smoke)), "MLflow smoke mismatch")
        report["mlflow_smoke_test"] = "passed, 5 rows"
        report["class_order"] = classes.tolist()

        for name in ("validation", "test"):
            frame = data[name]
            x = frame[FEATURES]
            y = frame[TARGET].to_numpy(dtype=int)
            pred = np.asarray(model.predict(x))
            require(pred.shape == y.shape and set(np.unique(pred)).issubset({False, True}),
                    "Unexpected predictions")
            probabilities = np.asarray(model.predict_proba(x))
            require(probabilities.shape == (len(x), 2) and np.isfinite(probabilities).all(),
                    "Invalid probabilities")
            require(((probabilities >= 0) & (probabilities <= 1)).all()
                    and np.allclose(probabilities.sum(axis=1), 1), "Invalid probability range")
            probability = probabilities[:, positive_index]
            pred = pred.astype(int)
            tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
            metrics = {
                "rows": len(y), "positive_cases": int(y.sum()),
                "roc_auc": float(roc_auc_score(y, probability)),
                "average_precision": float(average_precision_score(y, probability)),
                "accuracy": float(accuracy_score(y, pred)),
                "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
                "precision_positive": float(precision_score(y, pred, zero_division=0)),
                "recall_positive": float(recall_score(y, pred, zero_division=0)),
                "specificity": float(tn / (tn + fp)),
                "f1_positive": float(f1_score(y, pred, zero_division=0)),
                "brier_score": float(brier_score_loss(y, probability)),
                "log_loss": float(log_loss(y, probability, labels=[0, 1])),
                "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
                "baseline_always_no_default_accuracy": float((y == 0).mean()),
            }
            require(tp + tn + fp + fn == len(y), "Confusion matrix does not reconcile")
            require(abs(metrics["accuracy"] - (tp + tn) / len(y)) < 1e-12, "Accuracy audit failed")
            require(abs(metrics["recall_positive"] - tp / (tp + fn)) < 1e-12, "Recall audit failed")
            report[name] = metrics
            if name == "validation":
                require(abs(metrics["roc_auc"] - 0.7862939378883647) < 1e-6,
                        "Validation AUC not reproduced; test will not be evaluated")
                require(abs(metrics["accuracy"] - 0.8173076923076923) < 1e-12,
                        "Validation accuracy not reproduced; test will not be evaluated")
            print(name, json.dumps(metrics), flush=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Evaluation complete. No model fitting, cloud calls, or production deployment.", flush=True)


if __name__ == "__main__":
    main()
