import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = Path(__file__).parent / "data"
emails = {e["id"]: e for e in json.loads((D / "real_emails.json").read_text(encoding="utf-8"))}
rows = json.loads((D / "last_real_run.json").read_text(encoding="utf-8"))
labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))

PAIRS = {("LOW_PRIORITY", "TRASH"), ("LOW_PRIORITY", "IMPORTANT")}
for r in rows:
    now = labels[r["id"]]["label"]  # current label, after your fixes
    if (now, r["got"]) in PAIRS:
        e = emails[r["id"]]
        print(f"{now} -> {r['got']}  {e['from'][:40]}")
        print(f"   subject: {e['subject'][:90]}")
        print(f"   reason:  {r['reason'][:160]}\n")