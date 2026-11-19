"""Fetch a fresh held-out set. Appends to data/real_emails.json.

split values added:
  heldout2  - random sample from the last 60 days (same query as before)
  primary   - random sample of category:primary mail from the last 180 days
Ids already in the file are never fetched again.
"""
import json
import random
import shutil
import time

import fetch_emails as fe
from gmail_client import get_service

SEED = 7                      # different from the original 42
N_RANDOM = 100
N_PRIMARY = 40
PRIMARY_QUERY = "category:primary newer_than:180d -in:sent -in:drafts -in:spam -in:trash"


def list_ids_for(service, query: str) -> list[str]:
    old = fe.QUERY
    fe.QUERY = query
    try:
        return fe.list_ids(service)
    finally:
        fe.QUERY = old


def main() -> None:
    existing = json.loads(fe.OUT.read_text(encoding="utf-8"))
    seen = {e["id"] for e in existing}
    shutil.copy(fe.OUT, fe.OUT.with_name("real_emails_before_v2.json"))

    service = get_service()
    rng = random.Random(SEED)

    pool = [i for i in list_ids_for(service, fe.QUERY) if i not in seen]
    random_pick = rng.sample(pool, min(N_RANDOM, len(pool)))
    chosen = set(random_pick)

    primary_pool = [i for i in list_ids_for(service, PRIMARY_QUERY) if i not in seen and i not in chosen]
    primary_pick = rng.sample(primary_pool, min(N_PRIMARY, len(primary_pool)))

    plan = [(i, "heldout2") for i in random_pick] + [(i, "primary") for i in primary_pick]
    print(f"random: {len(random_pick)}  primary: {len(primary_pick)}")

    new = []
    for n, (msg_id, split) in enumerate(plan):
        e = fe.fetch_with_retry(service, msg_id)
        e["split"] = split
        new.append(e)
        time.sleep(0.2)
        if (n + 1) % 25 == 0:
            print(f"  fetched {n + 1}/{len(plan)}")

    fe.OUT.write_text(json.dumps(existing + new, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"added {len(new)} emails; file now has {len(existing) + len(new)}")


if __name__ == "__main__":
    main()