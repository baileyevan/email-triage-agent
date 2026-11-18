import json
import sys

from label_email import CHOICES, EMAILS, load_labels, save_labels, show

PROMPT = "current: {cur}  |  1-6 to change, Enter to keep, q quit > "


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python relabel.py <part of sender, e.g. amazon.com>")
        return
    needle = sys.argv[1].lower()
    emails = json.loads(EMAILS.read_text(encoding="utf-8"))
    labels = load_labels()
    matches = [e for e in emails if needle in e["from"].lower()]
    print(f"{len(matches)} emails match '{needle}'")

    for n, e in enumerate(matches, 1):
        show(e, n, len(matches))
        raw = input("\n" + PROMPT.format(cur=labels[e["id"]]["label"])).strip()
        if raw.lower() == "q":
            break
        if raw in CHOICES:
            labels[e["id"]] = {"label": CHOICES[raw], "hesitant": False}
            save_labels(labels)

    print("saved")


if __name__ == "__main__":
    main()