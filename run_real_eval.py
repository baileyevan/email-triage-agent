import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from classifier import classify

D = Path(__file__).parent / "data"
CATS = ["MUST_SEE", "IMPORTANT", "LOW_PRIORITY", "TRASH", "UNSURE"]
K = 5  # number of retrieved examples when --retrieval is used


def main() -> None:
    split = "dev"
    if "--split" in sys.argv:
        split = sys.argv[sys.argv.index("--split") + 1]
    elif "--heldout" in sys.argv:
        split = "heldout"
    use_retrieval = "--retrieval" in sys.argv

    all_emails = json.loads((D / "real_emails.json").read_text(encoding="utf-8"))
    labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))
    emails = [e for e in all_emails if e["split"] == split]

    pool = None
    if use_retrieval:
        from retrieval import ExamplePool
        # The pool is always built from DEV emails only. Held-out emails never enter it.
        pool = ExamplePool([{**e, "label": labels[e["id"]]["label"]}
                            for e in all_emails if e["split"] == "dev"])

    mode = f"retrieval (k={K})" if use_retrieval else "baseline (no examples)"
    print(f"evaluating {len(emails)} emails from the {split} split, mode: {mode}")

    rows = []
    for i, e in enumerate(emails, 1):
        # exclude_id makes it leave-one-out: a dev email can never retrieve itself
        examples = pool.similar(e, k=K, exclude_id=e["id"]) if pool else None
        r = classify(e, examples)
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

    matrix = defaultdict(Counter)
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
    buried = [r["id"] for r in rows if r["expected"] in worth_seeing and r["got"] in {"LOW_PRIORITY", "TRASH"}]
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