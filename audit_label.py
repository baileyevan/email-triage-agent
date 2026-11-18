import json
import re
from collections import Counter, defaultdict
from pathlib import Path

D = Path(__file__).parent / "data"
emails = json.loads((D / "real_emails.json").read_text(encoding="utf-8"))
labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))

by_domain = defaultdict(Counter)
for e in emails:
    m = re.search(r"@([\w.-]+)", e["from"])
    dom = m.group(1).lower() if m else "?"
    by_domain[dom][labels[e["id"]]["label"]] += 1

top = sorted(by_domain.items(), key=lambda kv: -sum(kv[1].values()))[:12]
for dom, c in top:
    print(f"{sum(c.values()):3} {dom:40} {dict(c)}")