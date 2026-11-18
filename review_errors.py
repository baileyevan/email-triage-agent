import json
import sys
from pathlib import Path

from label_email import CHOICES, load_labels, save_labels, show

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = Path(__file__).parent / "data"
VERDICTS = D / "error_review.json"
PROMPT = "m = model wrong, s = spec unclear, l = my label was wrong, Enter = skip, q = quit > "


def main() -> None:
    want_exp = sys.argv[1] if len(sys.argv) > 1 else None
    want_got = sys.argv[2] if len(sys.argv) > 2 else None

    emails = {e["id"]: e for e in json.loads((D / "real_emails.json").read_text(encoding="utf-8"))}
    rows = json.loads((D / "last_real_run.json").read_text(encoding="utf-8"))
    labels = load_labels()
    verdicts = json.loads(VERDICTS.read_text(encoding="utf-8")) if VERDICTS.exists() else {}

    errors = [r for r in rows if r["expected"] != r["got"]
              and (want_exp is None or r["expected"] == want_exp)
              and (want_got is None or r["got"] == want_got)
              and r["id"] not in verdicts]
    print(f"{len(errors)} errors to review")

    for n, r in enumerate(errors, 1):
        show(emails[r["id"]], n, len(errors))
        print("-" * 70)
        print(f"you labeled: {r['expected']}   model said: {r['got']}")
        print(f"model's reason: {r['reason']}")
        raw = input("\n" + PROMPT).strip().lower()
        if raw == "q":
            break
        if raw in ("m", "s"):
            verdicts[r["id"]] = {"verdict": raw, "expected": r["expected"], "got": r["got"]}
        elif raw == "l":
            new = input("new label 1-6 > ").strip()
            if new in CHOICES:
                labels[r["id"]] = {"label": CHOICES[new], "hesitant": False}
                save_labels(labels)
                verdicts[r["id"]] = {"verdict": "l", "expected": r["expected"], "got": r["got"]}
        VERDICTS.write_text(json.dumps(verdicts, indent=2), encoding="utf-8")

    from collections import Counter
    print("\nverdicts so far:", dict(Counter(v["verdict"] for v in verdicts.values())))


if __name__ == "__main__":
    main()