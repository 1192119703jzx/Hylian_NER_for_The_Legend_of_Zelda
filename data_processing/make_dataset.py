
import random, json
from pathlib import Path
from collections import defaultdict

random.seed(42)          # reproducibility

FILES = {
    "CHAR": Path("botw_cleaned_chars3.txt"),
    "LOC" : Path("botw_cleaned_locs3.txt"),
    "CREA": Path("synthetic_crea_processed.txt"),
    "ITEM": Path("synthetic_item_processed.txt"),
}

# target sizes (set to None to keep all)
KEEP = {"CHAR": 450, "LOC": 450, "CREA": None, "ITEM": None}

records = []                             # list of {"tokens": [...], "label": "CHAR", "text": "..."}
for label, path in FILES.items():
    with path.open(encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if KEEP[label]:
        lines = random.sample(lines, KEEP[label])
    for line in lines:
        tokens = line.split()            # crude whitespace split; refine later if needed
        records.append({"tokens": tokens, "label": label, "text": line})

# ---- shuffle & split -------------------------------------------------------
random.shuffle(records)
n = len(records)
train, dev, test = records[: int(.8*n)], records[int(.8*n): int(.9*n)], records[int(.9*n):]

# ---- write JSON Lines ------------------------------------------------------
def write_jsonl(lst, fname):
    with open(fname, "w", encoding="utf-8") as f:
        for ex in lst:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

write_jsonl(train, "train.jsonl")
write_jsonl(dev,   "dev.jsonl")
write_jsonl(test,  "test.jsonl")

print(f"Dataset sizes → train {len(train)}, dev {len(dev)}, test {len(test)}  (total {n})")
