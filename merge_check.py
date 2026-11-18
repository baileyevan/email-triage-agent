import json
from collections import Counter
from pathlib import Path

D = Path(__file__).parent / "data"
rows = json.loads((D / "last_real_run.json").read_text(encoding="utf-8"))
labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))

MERGE = {"REVIEW": "LOW_PRIORITY"}
CATS = ["MUST_SEE", "IMPORTANT", "REVIEW", "LOW_PRIORITY", "TRASH", "UNSURE"]


def score(merge: bool):
    ok = 0
    matrix = {c: Counter() for c in CATS}
    for r in rows:
        exp, got = labels[r["id"]]["label"], r["got"]
        if merge:
            exp, got = MERGE.get(exp, exp), MERGE.get(got, got)
        ok += exp == got
        matrix[exp][got] += 1
    return ok, matrix


before, _ = score(False)
after, matrix = score(True)
print(f"current categories:        {before}/{len(rows)}")
print(f"REVIEW merged into LOW:    {after}/{len(rows)}")

print("\nmerged matrix (rows = your label, columns = model):")
cols = [c for c in CATS if c != "REVIEW"]
print(f"{'':14}" + "".join(f"{c[:7]:>9}" for c in cols))
for exp in cols:
    print(f"{exp:14}" + "".join(f"{matrix[exp][g]:>9}" for g in cols))