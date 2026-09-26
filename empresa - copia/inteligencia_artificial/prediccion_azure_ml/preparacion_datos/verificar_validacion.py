"""Independent saved-file, audit, source preservation and rerun checks."""
import csv
import hashlib
import subprocess
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream)
        return next(reader), list(reader)


def hashes(paths):
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


header, original = read(BASE / "datos_uci/entrenamiento.csv")
parts = {}
for name, count in (("entrenamiento_reducido", 17909), ("validacion", 6136)):
    folder = BASE / "carga_azure" / name
    h, rows = read(folder / f"{name}.csv")
    assert h == header and len(rows) == count
    assert {r[-1] for r in rows} == {"0", "1"}
    assert all(len(r) == 20 for r in rows)
    assert {p.name for p in folder.iterdir()} == {"MLTable", f"{name}.csv"}
    assert f"file: ./{name}.csv" in (folder / "MLTable").read_text()
    parts[name] = rows
assert Counter(map(tuple, original)) == Counter(tuple(r) for rows in parts.values() for r in rows)
_, audit = read(BASE / "datos_uci/auditoria_validacion.csv")
assert sorted(int(a[0]) for a in audit) == list(range(2, len(original) + 2))
for name, rows in parts.items():
    assert Counter(tuple(original[int(a[0]) - 2]) for a in audit if a[1] == name) == Counter(map(tuple, rows))
_, parts["prueba"] = read(BASE / "datos_uci/prueba.csv")
for left, right in combinations(parts, 2):
    assert not {tuple(r[:-1]) for r in parts[left]} & {tuple(r[:-1]) for r in parts[right]}
paths = list((BASE / "datos_uci").glob("*.*")) + [p for p in (BASE / "carga_azure").rglob("*") if p.is_file()]
before = hashes(paths)
subprocess.run([sys.executable, str(Path(__file__).with_name("preparar_validacion.py"))], check=True, capture_output=True)
assert before == hashes(paths)
assert before[str(BASE / "datos_uci/prueba.csv")] == "d7cf431db3eb63400d72a5cfca20d679396013ccc18ff5c902ff71215b01fb72"
print("OK: 17,909 train + 6,136 validation; 5,955 test unchanged; disjoint predictors, intact labels, complete audit, reproducible outputs.")
