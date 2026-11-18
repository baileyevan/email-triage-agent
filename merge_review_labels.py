import json
import shutil
from pathlib import Path

D = Path(__file__).parent / "data"
path = D / "labels.json"
shutil.copy(path, D / "labels_before_review_merge.json")

labels = json.loads(path.read_text(encoding="utf-8"))
n = 0
for v in labels.values():
    if v["label"] == "REVIEW":
        v["label"] = "LOW_PRIORITY"
        n += 1
path.write_text(json.dumps(labels, indent=2), encoding="utf-8")
print(f"merged {n} REVIEW labels into LOW_PRIORITY (backup: labels_before_review_merge.json)")