import json
from collections import Counter
from pathlib import Path

labels = json.loads((Path(__file__).parent / "data" / "labels.json").read_text(encoding="utf-8"))
print("labeled:", len(labels))
print(Counter(v["label"] for v in labels.values()))
print("hesitant:", sum(v["hesitant"] for v in labels.values()))