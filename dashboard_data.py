"""Builds the dashboard payload from saved data. No API calls, no cost.

Category for each email:
  - the model's answer from a saved run file (data/run_*_v9.json) if one exists
  - otherwise your own label from data/labels.json
`source` says which, so the UI never presents a hand label as a model result.
"""
import json
import re
from pathlib import Path

CATEGORIES = ["MUST_SEE", "IMPORTANT", "LOW_PRIORITY", "UNSURE", "TRASH"]
PREVIEW_CHARS = 200


def _preview(body: str) -> str:
    return re.sub(r"\s+", " ", body).strip()[:PREVIEW_CHARS]


def _category(raw: str) -> str:
    raw = "LOW_PRIORITY" if raw == "REVIEW" else raw
    return raw if raw in CATEGORIES else "UNSURE"


def load_dashboard(data_dir: Path) -> dict:
    emails = json.loads((data_dir / "real_emails.json").read_text(encoding="utf-8"))
    labels = json.loads((data_dir / "labels.json").read_text(encoding="utf-8"))

    decisions = {}
    for path in sorted(data_dir.glob("run_*_v9.json")):
        for row in json.loads(path.read_text(encoding="utf-8")):
            decisions[row["id"]] = row

    groups = {c: [] for c in CATEGORIES}
    for e in emails:
        row = decisions.get(e["id"])
        if row:
            category, reason, source = _category(row["got"]), row.get("reason", ""), "model"
        elif e["id"] in labels:
            category, reason, source = _category(labels[e["id"]]["label"]), "", "my label"
        else:
            continue
        groups[category].append({
            "id": e["id"],
            "sender": e["from"],
            "subject": e["subject"],
            "received": e["received"],
            "preview": _preview(e["body"]),
            "reason": reason,
            "source": source,
        })

    for items in groups.values():
        items.sort(key=lambda i: i["received"], reverse=True)

    return {
        "total": sum(len(v) for v in groups.values()),
        "counts": {c: len(groups[c]) for c in CATEGORIES},
        "categories": groups,
    }
