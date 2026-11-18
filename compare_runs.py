import json
import sys
from pathlib import Path

D = Path(__file__).parent / "data"
E = {e["id"]: e for e in json.loads((D / "real_emails.json").read_text(encoding="utf-8"))}
old = {r["id"]: r for r in json.loads((D / sys.argv[1]).read_text(encoding="utf-8"))}
new = {r["id"]: r for r in json.loads((D / sys.argv[2]).read_text(encoding="utf-8"))}
labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))


def norm(c):
    return "LOW_PRIORITY" if c == "REVIEW" else c


for i in new:
    if i in old and norm(old[i]["got"]) != norm(new[i]["got"]):
        print(f"you: {labels[i]['label']:12} old: {norm(old[i]['got']):12} new: {norm(new[i]['got']):12} "
              f"{E[i]['from'][:28]} | {E[i]['subject'][:55]}")