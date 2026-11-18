import json
import sys
from collections import Counter
from pathlib import Path

from classifier import classify

D = Path(__file__).parent / "data"
CATS = ["MUST_SEE", "IMPORTANT", "REVIEW", "LOW_PRIORITY", "TRASH", "UNSURE"]


def main() -> None:
    split = "heldout" if "--heldout" in sys.argv else "dev"
    emails = [e for e in json.loads((D / "real_emails.json").read_text(encoding="utf-8"))
              if e["split"] == split]
    labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))
    print(f"evaluating {len(emails)} emails from the {split} split")

    rows = []
    for i, e in enumerate(emails, 1):
        r = classify(e)
        rows.append({
            "id": e["id"],
            "expected": labels[e["id"]]["label"],
            "hesitant": labels[e["id"]]["hesitant"],
            "got": r.category.value,
            "source": r.source,
            "failure": r.failure,
            "reason": r.reason,
        })
        if i % 20 == 0:
            print(f"  {i}/{len(emails)}")

    total = len(rows)
    correct = sum(r["expected"] == r["got"] for r in rows)
    majority = Counter(r["expected"] for r in rows).most_common(1)[0]

    matrix = {c: Counter() for c in CATS}
    for r in rows:
        matrix[r["expected"]][r["got"]] += 1

    print(f"\naccuracy: {correct}/{total}   (always answering {majority[0]} scores {majority[1]}/{total})")
    print("\nrows = what you labeled, columns = what the model said")
    print(f"{'':14}" + "".join(f"{c[:7]:>9}" for c in CATS))
    for exp in CATS:
        print(f"{exp:14}" + "".join(f"{matrix[exp][g]:>9}" for g in CATS))

    print("\nper category:")
    for c in CATS:
        n_exp = sum(matrix[c].values())
        n_got = sum(matrix[e][c] for e in CATS)
        hit = matrix[c][c]
        recall = f"{hit}/{n_exp}" if n_exp else "-"
        precision = f"{hit}/{n_got}" if n_got else "-"
        print(f"  {c:13} recall {recall:8} precision {precision}")

    worth_seeing = {"MUST_SEE", "IMPORTANT"}
    buried = [r["id"] for r in rows if r["expected"] in worth_seeing and r["got"] in {"REVIEW", "LOW_PRIORITY", "TRASH"}]
    to_trash = [r["id"] for r in rows if r["expected"] not in {"TRASH", "UNSURE"} and r["got"] == "TRASH"]
    false_alarms = [r["id"] for r in rows if r["expected"] in {"TRASH", "LOW_PRIORITY"} and r["got"] in worth_seeing]
    fallbacks = sum(r["source"] == "fallback" for r in rows)

    print(f"\nimportant mail buried (IMPORTANT/MUST_SEE -> lower): {len(buried)} {buried}")
    print(f"worth-keeping mail sent to TRASH:                    {len(to_trash)} {to_trash}")
    print(f"junk surfaced as important (false alarms):           {len(false_alarms)}")
    print(f"fallbacks: {fallbacks}")

    (D / "last_real_run.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nsaved to {D / 'last_real_run.json'}")


if __name__ == "__main__":
    main()