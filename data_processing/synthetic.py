import json, re, unicodedata
from pathlib import Path

SRC      = Path("hyrule_compendium_entities.json")
OUT_CRE  = Path("synthetic_crea.txt")
OUT_ITEM = Path("synthetic_item.txt")

PRONOUN_RE = re.compile(r"\b(these|they|it|this|those)\b", flags=re.I)

def normalise(t: str) -> str:
    t = unicodedata.normalize("NFC", t)
    return re.sub(r"[ \t]{2,}", " ", t).strip()

def maybe_fix(sentence: str, name: str) -> str | None:
    """
    • If <name> already in sentence → keep.
    • Else replace the *first* pronoun match anywhere.
    • If still no name → drop the sentence (return None).
    """
    if re.search(rf"\b{re.escape(name)}\b", sentence, re.I):
        return sentence

    # replace first pronoun occurrence
    new_sent, n_sub = PRONOUN_RE.subn(name, sentence, count=1)
    if n_sub and re.search(rf"\b{re.escape(name)}\b", new_sent, re.I):
        return new_sent

    return None  


CREA = {"creatures", "monsters"}
ITEM = {"equipment", "materials", "treasures", "items"}

crea_f = OUT_CRE.open("w", encoding="utf-8")
item_f = OUT_ITEM.open("w", encoding="utf-8")

for rec in json.loads(SRC.read_text(encoding="utf-8")):
    name = rec["name"].strip()
    cat  = rec["category"].lower()

    for raw in rec["description"].split("."):
        raw = raw.strip()
        if not raw:
            continue
        fixed = maybe_fix(normalise(raw) + ".", name)
        if fixed is None:
            continue
        if cat in CREA:
            crea_f.write(fixed + "\n")
        elif cat in ITEM:
            item_f.write(fixed + "\n")

crea_f.close(); item_f.close()
print("Finished — sentences written to", OUT_CRE, "and", OUT_ITEM)
