import json
import re
from collections import Counter
from pathlib import Path

D = Path(__file__).parent / "data"
emails = {e["id"]: e for e in json.loads((D / "real_emails.json").read_text(encoding="utf-8"))}
rows = json.loads((D / "last_real_run.json").read_text(encoding="utf-8"))

counts = Counter()
for r in rows:
    if r["expected"] == r["got"]:
        continue
    m = re.search(r"@([\w.-]+)", emails[r["id"]]["from"])
    counts[(r["expected"], r["got"], m.group(1).lower() if m else "?")] += 1

for (exp, got, dom), n in sorted(counts.items(), key=lambda kv: -kv[1]):
    print(f"{n:3}  {exp:13} -> {got:13} {dom}")