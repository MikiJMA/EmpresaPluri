"""Split only the existing training data; preserve the original test holdout."""
import csv
import hashlib
import io
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SEED = "plurione-validacion-agrupada-v1"
EXPECTED = {
    "entrenamiento.csv": "0fb503f50bf89640d1e12ad7387e22f0daada4eccc57fa1d58337b5279c6d8ab",
    "prueba.csv": "d7cf431db3eb63400d72a5cfca20d679396013ccc18ff5c902ff71215b01fb72",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse(data):
    rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
    header, rows = rows[0], rows[1:]
    if len(header) != 20 or header[-1] != "incumplimiento_mes_siguiente":
        raise ValueError("Unexpected schema")
    if any(len(r) != 20 or any(v == "" for v in r) for r in rows):
        raise ValueError("Missing values or malformed rows")
    # All columns are integers; validate without altering original strings.
    for row in rows:
        for value in row:
            int(value)
        if row[-1] not in ("0", "1"):
            raise ValueError("Invalid label")
    return header, rows


def csv_bytes(header, rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def main():
    sources = {name: (BASE / "datos_uci" / name).read_bytes() for name in EXPECTED}
    for name, raw in sources.items():
        if sha(raw) != EXPECTED[name]:
            raise ValueError(f"Source changed: {name}; review before splitting")
    header, training = parse(sources["entrenamiento.csv"])
    test_header, test = parse(sources["prueba.csv"])
    assert header == test_header
    parts = {"entrenamiento_reducido": [], "validacion": []}
    audit = []
    for index, row in enumerate(training, start=2):
        key = sha((SEED + ":" + ",".join(row[:-1])).encode())
        name = "validacion" if int(key, 16) < 2**256 // 4 else "entrenamiento_reducido"
        parts[name].append(row)
        audit.append([index, name, key])
    assert Counter(map(tuple, training)) == Counter(map(tuple, parts["entrenamiento_reducido"] + parts["validacion"]))
    sets = {name: {tuple(r[:-1]) for r in rows} for name, rows in {**parts, "prueba": test}.items()}
    for left, right in combinations(sets, 2):
        assert not sets[left] & sets[right], f"Predictor overlap: {left}/{right}"
    template = (BASE / "carga_azure/entrenamiento/MLTable").read_text(encoding="utf-8")
    assert template.count("./entrenamiento.csv") == 1
    report = {
        "seed": SEED, "method": "SHA256 by 19 predictors, 25% group probability to validation; not temporal or stratified",
        "source_sha256": EXPECTED, "source_training_rows": len(training),
        "test_rows_unchanged": len(test), "pairwise_predictor_overlap": 0,
        "target": header[-1], "partitions": {},
    }
    outputs = {}
    for name, rows in parts.items():
        assert set(r[-1] for r in rows) == {"0", "1"}
        folder = BASE / "carga_azure" / name
        payload = csv_bytes(header, rows)
        outputs[folder / f"{name}.csv"] = payload
        outputs[folder / "MLTable"] = template.replace("./entrenamiento.csv", f"./{name}.csv").encode("utf-8")
        report["partitions"][name] = {
            "rows": len(rows), "class_counts": dict(Counter(r[-1] for r in rows)),
            "sha256": sha(payload), "columns": len(header),
        }
    outputs[BASE / "datos_uci/auditoria_validacion.csv"] = csv_bytes(["linea_entrenamiento_original", "particion", "grupo_sha256"], audit)
    outputs[BASE / "datos_uci/division_validacion.json"] = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    # Idempotent; never silently overwrite different user content.
    for path, payload in outputs.items():
        if path.exists() and path.read_bytes() != payload:
            raise FileExistsError(f"Different output exists: {path}")
    for path, payload in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(payload)
        assert path.read_bytes() == payload
    for name, raw in sources.items():
        assert (BASE / "datos_uci" / name).read_bytes() == raw
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
