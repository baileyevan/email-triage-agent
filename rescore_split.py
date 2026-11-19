import json, sys
from collections import Counter, defaultdict
from pathlib import Path

D = Path(__file__).parent / "data"
labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))
CATS = ["MUST_SEE", "IMPORTANT", "LOW_PRIORITY", "TRASH", "UNSURE"]
FIX = {"REVIEW": "LOW_PRIORITY"}   # merged category

for name in sys.argv[1:]:
    rows = json.loads((D / name).read_text(encoding="utf-8"))
    m = defaultdict(Counter)
    for r in rows:
        exp = labels[r["id"]]["label"]
        exp = FIX.get(exp, exp)
        m[exp][r["got"]] += 1
    n = len(rows)
    ok = sum(m[c][c] for c in CATS)
    trash = sum(m["TRASH"].values())
    print(f"\n{name}: {ok}/{n}   (always-TRASH: {trash}/{n})")
    print(f"{'':14}" + "".join(f"{c[:7]:>9}" for c in CATS))
    for e in CATS:
        print(f"{e:14}" + "".join(f"{m[e][g]:>9}" for g in CATS))
    junk = sum(m["TRASH"].values())
    print(f"  TRASH surfaced as IMPORTANT/MUST_SEE: {m['TRASH']['IMPORTANT'] + m['TRASH']['MUST_SEE']}/{junk}")
    print(f"  TRASH promoted to LOW_PRIORITY:       {m['TRASH']['LOW_PRIORITY']}/{junk}")
    print(f"  worth-keeping sent to TRASH:          {sum(m[e]['TRASH'] for e in ('MUST_SEE','IMPORTANT','LOW_PRIORITY'))}")