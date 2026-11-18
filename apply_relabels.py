import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = Path(__file__).parent / "data"
emails = json.loads((D / "real_emails.json").read_text(encoding="utf-8"))
labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))


def li(sender):
    return "linkedin.com" in sender


# (new label, predicate on lowercase sender and subject)
RULES = [
    ("LOW_PRIORITY", lambda f, s: "alerts@ziprecruiter.com" in f),
    ("LOW_PRIORITY", lambda f, s: li(f) and re.search(r"developer insights", s)),
    ("IMPORTANT", lambda f, s: li(f) and re.fullmatch(r"you have \d+ new messages?", s.strip())),
    ("TRASH", lambda f, s: li(f) and re.search(r"viewed your profile|open to work|just posted something|connections, experience|hired near you|accepted your invitation", s)),
    ("TRASH", lambda f, s: "via handshake" in f and re.search(r"looking for your next opportunity|reminder: apply today|spark your interest", s)),
    ("TRASH", lambda f, s: "facebookmail.com" in f and "notifications about" in s),
    ("TRASH", lambda f, s: "academia-mail.com" in f),
    ("TRASH", lambda f, s: "feedback.uhc.com" in f),
]

changes = []
for e in emails:
    f, s = e["from"].lower(), e["subject"].lower()
    for new, test in RULES:
        if test(f, s):
            cur = labels[e["id"]]["label"]
            if cur != new:
                changes.append((e, cur, new))
            break

print(f"{len(changes)} labels would change:\n")
for e, cur, new in changes:
    print(f"[{e['split']:7}] {cur:13} -> {new:13} {e['from'][:28]:28} | {e['subject'][:60]}")

if changes and input("\napply these changes? (y/n) > ").strip().lower() == "y":
    for e, cur, new in changes:
        labels[e["id"]] = {"label": new, "hesitant": False}
    (D / "labels.json").write_text(json.dumps(labels, indent=2), encoding="utf-8")
    print("applied")
else:
    print("nothing changed")