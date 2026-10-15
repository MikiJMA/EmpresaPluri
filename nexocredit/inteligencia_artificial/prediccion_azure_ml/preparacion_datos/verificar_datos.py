"""Independent checks of produced CSVs and deterministic regeneration."""
import csv
import hashlib
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "datos_uci"


def read(name):
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


original = read("original_uci.csv")
train, test = read("entrenamiento.csv"), read("prueba.csv")
assert (len(original), len(train), len(test)) == (30000, 24045, 5955)
target = "incumplimiento_mes_siguiente"
features = list(train[0])[:-1]
assert len(features) == 19 and list(train[0])[-1] == target
assert list(test[0]) == list(train[0])
for rows in (train, test):
    assert all(len(row) == 20 and all(v not in (None, "") for v in row.values()) for row in rows)
    assert all(int(v) == float(v) for row in rows for v in row.values())
    assert {r[target] for r in rows} == {"0", "1"}
assert not {tuple(r[k] for k in features) for r in train} & {tuple(r[k] for k in features) for r in test}
expected = Counter(tuple(str(int(r[f"X{i}"])) for i in [1] + list(range(6, 24))) + (r["Y"],) for r in original)
actual = Counter(tuple(r.values()) for r in train + test)
assert actual == expected, "Lost or changed original observations"
audit = read("auditoria_particiones.csv")
assert len(audit) == 30000
assert {r["ID_original"] for r in audit} == {r["ID"] for r in original}
assert Counter(r["particion"] for r in audit) == {"entrenamiento": len(train), "prueba": len(test)}
by_id = {r["ID"]: r for r in original}
for name, rows in (("entrenamiento", train), ("prueba", test)):
    rebuilt = Counter(tuple(str(int(by_id[a["ID_original"]][f"X{i}"])) for i in [1] + list(range(6, 24))) + (by_id[a["ID_original"]]["Y"],) for a in audit if a["particion"] == name)
    assert rebuilt == Counter(tuple(r.values()) for r in rows)
files = sorted(ROOT.glob("*.csv")) + [ROOT / "validacion.json"]
before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
subprocess.run([sys.executable, str(Path(__file__).with_name("preparar_uci.py"))], check=True, capture_output=True)
after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
assert before == after, "Non-reproducible output"
print("OK: 30,000 rows; labels and audit conserved; no predictor overlap; reproducible hashes.")
