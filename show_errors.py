import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = Path(__file__).parent / "data"
emails = {e["id"]: e for e in json.loads((D / "real_emails.json").read_text(encoding="utf-8"))}
rows = json.loads((D / sys.argv[1]).read_text(encoding="utf-8"))

for r in rows:
    if r["expected"] != r["got"]:
        e = emails[r["id"]]
        print(f"{r['expected']} -> {r['got']}  [{r['id']}]  {e['from'][:36]}")
        print(f"   subject: {e['subject'][:80]}")
        print(f"   reason:  {r['reason'][:150]}\n")