import json
from collections import Counter, defaultdict
from pathlib import Path

D = Path(__file__).parent / "data"
emails = json.loads((D / "real_emails.json").read_text(encoding="utf-8"))
labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))
FIX = {"REVIEW": "LOW_PRIORITY"}

GROUPS = {
    "job sites (handshake/ziprecruiter/indeed)": lambda e: any(k in e["from"].lower() for k in ("handshake", "ziprecruiter", "indeed")),
    "linkedin job emails":                       lambda e: "linkedin" in e["from"].lower() and any(k in e["subject"].lower() for k in ("jobs", "job openings", "hiring")),
    "linkedin 'new message(s)'":                 lambda e: "linkedin" in e["from"].lower() and "new message" in e["subject"].lower(),
    "nick singh newsletter":                     lambda e: "nicksingh" in e["from"].lower(),
    "steam":                                     lambda e: "steampowered" in e["from"].lower(),
}

for name, test in GROUPS.items():
    print(f"\n{name}")
    by = defaultdict(Counter)
    for e in emails:
        if test(e) and e["id"] in labels:
            lab = FIX.get(labels[e["id"]]["label"], labels[e["id"]]["label"])
            by[e["split"]][lab] += 1
    for split in ("dev", "heldout", "heldout2", "primary"):
        if by[split]:
            print(f"  {split:9} {dict(by[split])}")