"""Prepare an academic UCI holdout without external Python dependencies."""
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1] / "datos_uci"
URL = "https://archive.ics.uci.edu/static/public/350/data.csv"
SEED = "plurione-uci350-v1"
SOURCE_SHA256 = "45bcf4df62ff2e237a74eb155cabfb4bbbc171219a0637daef44fdad07503dd0"
FEATURES = ["LIMIT_BAL", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
FEATURES += [f"BILL_AMT{i}" for i in range(1, 7)]
FEATURES += [f"PAY_AMT{i}" for i in range(1, 7)]
TARGET = "incumplimiento_mes_siguiente"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    original = ROOT / "original_uci.csv"
    if not original.exists():
        with urlopen(URL, timeout=60) as response:
            raw = response.read()
        original.write_bytes(raw)
    raw = original.read_bytes()
    if digest(raw) != SOURCE_SHA256:
        raise ValueError("La fuente cambió: revisar antes de regenerar las particiones.")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    assert reader.fieldnames == ["ID"] + [f"X{i}" for i in range(1, 24)] + ["Y"], reader.fieldnames
    source = list(reader)
    assert len(source) == 30000
    assert len({r["ID"] for r in source}) == len(source)
    groups = defaultdict(list)
    # Group identical retained predictors together, even with conflicting labels.
    # No labels participate in the split decision; all original rows are retained.
    for row in source:
        values = [int(row[f"X{i}"]) for i in [1] + list(range(6, 24))]
        label = int(row["Y"])
        assert label in (0, 1)
        groups[tuple(values)].append((row["ID"], label))
    partitions = {"entrenamiento": [], "prueba": []}
    membership = []
    group_sets = {name: set() for name in partitions}
    for values, members in sorted(groups.items()):
        key = digest((SEED + ":" + ",".join(map(str, values))).encode())
        # Deterministic approximately 80/20 split at predictor-group level.
        name = "prueba" if int(key, 16) < 2**256 // 5 else "entrenamiento"
        group_sets[name].add(key)
        for source_id, label in members:
            partitions[name].append(list(values) + [label])
            membership.append([source_id, name, key])
    assert not group_sets["entrenamiento"] & group_sets["prueba"]
    assert sum(map(len, partitions.values())) == len(source)
    report = {
        "source": URL,
        "citation": "Yeh, I. (2009). Default of Credit Card Clients. UCI Machine Learning Repository. https://doi.org/10.24432/C55S3H",
        "license": "CC BY 4.0; https://creativecommons.org/licenses/by/4.0/",
        "source_sha256": digest(raw),
        "seed": SEED,
        "split": "SHA256 of retained predictors; grouped approximate 80/20; not temporal or stratified",
        "rows": len(source),
        "predictors": FEATURES,
        "target": TARGET,
        "excluded": ["ID", "SEX", "EDUCATION", "MARRIAGE", "AGE"],
        "unique_predictor_groups": len(groups),
        "groups_with_multiple_rows": sum(len(v) > 1 for v in groups.values()),
        "groups_with_conflicting_labels": sum(len({label for _, label in v}) > 1 for v in groups.values()),
        "cross_partition_predictor_overlap": 0,
        "partitions": {},
    }
    for name, rows in partitions.items():
        path = ROOT / f"{name}.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(FEATURES + [TARGET])
            writer.writerows(rows)
        counts = Counter(row[-1] for row in rows)
        assert set(counts) == {0, 1}
        report["partitions"][name] = {
            "rows": len(rows), "class_counts": dict(counts),
            "default_fraction": counts[1] / len(rows),
            "sha256": digest(path.read_bytes()),
        }
    with (ROOT / "auditoria_particiones.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["ID_original", "particion", "grupo_sha256"])
        writer.writerows(membership)
    (ROOT / "validacion.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
