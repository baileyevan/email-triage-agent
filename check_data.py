import json
import re
from collections import Counter
from pathlib import Path

emails = json.loads((Path(__file__).parent / "data" / "real_emails.json").read_text(encoding="utf-8"))

print("total:", len(emails), dict(Counter(e["split"] for e in emails)))
print("empty bodies:", sum(1 for e in emails if not e["body"].strip()))
print("cut at 4000 chars:", sum(1 for e in emails if len(e["body"]) >= 4000))
print("no subject:", sum(1 for e in emails if not e["subject"].strip()))

domains = Counter()
for e in emails:
    m = re.search(r"@([\w.-]+)", e["from"])
    domains[m.group(1).lower() if m else "?"] += 1
print("top sender domains:")
for d, n in domains.most_common(12):
    print(f"  {n:3} {d}")