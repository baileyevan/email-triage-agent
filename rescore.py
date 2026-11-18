import json
from collections import Counter
from pathlib import Path

D = Path(__file__).parent / "data"
CATS = ["MUST_SEE", "IMPORTANT", "REVIEW", "LOW_PRIORITY", "TRASH", "UNSURE"]
rows = json.loads((D / "last_real_run.json").read_text(encoding="utf-8"))
labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))
for r in rows:
    r["expected"] = labels[r["id"]]["label"]

total = len(rows)
correct = sum(r["expected"] == r["got"] for r in rows)
major = Counter(r["expected"] for r in rows).most_common(1)[0]
print(f"accuracy: {correct}/{total}   (always {major[0]}: {major[1]}/{total})")

matrix = {c: Counter() for c in CATS}
for r in rows:
    matrix[r["expected"]][r["got"]] += 1
print(f"{'':14}" + "".join(f"{c[:7]:>9}" for c in CATS))
for exp in CATS:
    print(f"{exp:14}" + "".join(f"{matrix[exp][g]:>9}" for g in CATS))

for c in CATS:
    n_exp = sum(matrix[c].values())
    n_got = sum(matrix[e][c] for e in CATS)
    hit = matrix[c][c]
    print(f"  {c:13} recall {hit}/{n_exp}  precision {hit}/{n_got}")

buried = [r["id"] for r in rows if r["expected"] in {"MUST_SEE", "IMPORTANT"} and r["got"] in {"REVIEW", "LOW_PRIORITY", "TRASH"}]
to_trash = [r["id"] for r in rows if r["expected"] not in {"TRASH", "UNSURE"} and r["got"] == "TRASH"]
print(f"important buried: {len(buried)}   worth-keeping sent to TRASH: {len(to_trash)}")