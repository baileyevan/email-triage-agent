import json
from collections import Counter
from pathlib import Path

from classifier import classify

EMAILS_PATH = Path(__file__).parent / "evals" / "fake_emails.json"
RESULTS_PATH = Path(__file__).parent / "evals" / "last_run.json"

HIGH = {"MUST_SEE", "IMPORTANT"}
LOW = {"REVIEW", "LOW_PRIORITY", "TRASH"}


def main() -> None:
    emails = json.loads(EMAILS_PATH.read_text(encoding="utf-8"))
    rows = []

    for e in emails:
        r = classify(e)  # only classify() sees the email; it never reads label/notes
        rows.append({
            "id": e["id"],
            "expected": e["label"],
            "got": r.category.value,
            "source": r.source,
            "failure": r.failure,
            "reason": r.reason,
        })

    print(f"{'id':5} {'expected':13} {'got':13} {'src':9} ok")
    for row in rows:
        ok = "" if row["expected"] == row["got"] else "  <-- WRONG"
        print(f"{row['id']:5} {row['expected']:13} {row['got']:13} {row['source']:9}{ok}")

    total = len(rows)
    correct = sum(r["expected"] == r["got"] for r in rows)
    fallbacks = sum(r["source"] == "fallback" for r in rows)
    model_unsure = sum(r["source"] == "model" and r["got"] == "UNSURE" for r in rows)
    # the dangerous error: something I needed to see got filed as low value
    missed = [r["id"] for r in rows if r["expected"] in HIGH and r["got"] in LOW]

    print()
    print(f"accuracy:           {correct}/{total}")
    print(f"fallbacks:          {fallbacks}")
    print(f"UNSURE (model):     {model_unsure}")
    print(f"missed important:   {len(missed)} {missed}")
    print("got distribution:   ", dict(Counter(r["got"] for r in rows)))

    RESULTS_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nsaved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()