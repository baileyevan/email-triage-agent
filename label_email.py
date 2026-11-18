import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # real mail has emoji/odd characters

DATA = Path(__file__).parent / "data"
EMAILS = DATA / "real_emails.json"
LABELS = DATA / "labels.json"
PREVIEW = 1200
CHOICES = {"1": "MUST_SEE", "2": "IMPORTANT", "3": "REVIEW",
           "4": "LOW_PRIORITY", "5": "TRASH", "6": "UNSURE"}
PROMPT = ("\n1 MUST_SEE  2 IMPORTANT  3 REVIEW  4 LOW_PRIORITY  5 TRASH  6 UNSURE\n"
          "(add ? if hesitant)  m more  b back  q quit > ")


def load_labels() -> dict:
    return json.loads(LABELS.read_text(encoding="utf-8")) if LABELS.exists() else {}


def save_labels(labels: dict) -> None:
    LABELS.write_text(json.dumps(labels, indent=2), encoding="utf-8")


def show(e: dict, n: int, total: int, full: bool = False) -> None:
    body = e["body"] if full else e["body"][:PREVIEW]
    print("\n" + "=" * 70)
    print(f"[{n}/{total}]  from: {e['from']}")
    print(f"received: {e['received']}")
    print(f"subject: {e['subject']}")
    print("-" * 70)
    print(body)
    if not full and len(e["body"]) > PREVIEW:
        print(f"\n... ({len(e['body']) - PREVIEW} more characters, type m for all)")


def main() -> None:
    emails = json.loads(EMAILS.read_text(encoding="utf-8"))
    labels = load_labels()
    i, revisit = 0, False

    while i < len(emails):
        e = emails[i]
        if e["id"] in labels and not revisit:
            i += 1
            continue
        revisit = False
        show(e, i + 1, len(emails))

        while True:
            raw = input(PROMPT).strip().lower()
            if raw == "q":
                print(f"saved: {len(labels)}/{len(emails)} labeled")
                return
            if raw == "m":
                show(e, i + 1, len(emails), full=True)
                continue
            if raw == "b":
                if i > 0:
                    i -= 1
                    revisit = True
                break
            key = raw.rstrip("?")
            if key in CHOICES:
                labels[e["id"]] = {"label": CHOICES[key], "hesitant": raw.endswith("?")}
                save_labels(labels)
                i += 1
                break
            print("not understood")

    print(f"done: {len(labels)}/{len(emails)} labeled")


if __name__ == "__main__":
    main()