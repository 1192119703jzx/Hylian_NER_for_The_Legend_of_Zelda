 
"""
Generate two one‑sentence‑per‑line text files from
hyrule_compendium_entities.json:

  • synthetic_crea_processed.txt   (creatures / monsters)
  • synthetic_item_processed.txt   (items / equipment / etc.)

Rules applied, in order:

1.  Split each description on "."   (period + optional spaces).
2.  Ensure the entity name appears in the sentence:
      a) if it's already there, keep the sentence.
      b) else replace the first   they / it
         with the entity name.
      c) else replace the *token right after*
         this | these | those  with the entity name.
      d) else keep the sentence unchanged.
3.  Expand common verb contractions:
      're → are   ·   've → have   ·   'll → will   ·   's → is
4.  Unicode NFC normalisation + collapse multiple spaces → one.
"""

import json, re, unicodedata
from pathlib import Path

SRC_JSON  = Path("hyrule_compendium_entities.json")
OUT_CRE   = Path("synthetic_crea_processed.txt")
OUT_ITEM  = Path("synthetic_item_processed.txt")

CREA_CATS = {"creatures", "monsters"}
ITEM_CATS = {"equipment", "materials", "treasures"}


ENTITY_RE_TPL    = r"\b{}\b"

PRON_THEY_IT     = re.compile(r"\b(they|it)\b", flags=re.I)
PRON_THIS_THESE  = re.compile(r"\b(this|these|those)\s+(\w[\w\-]*)", flags=re.I)

CONTRACTIONS = [
    (re.compile(r"\b(\w+)'re\b", flags=re.I), r"\1 are"),
    (re.compile(r"\b(\w+)'ve\b", flags=re.I), r"\1 have"),
    (re.compile(r"\b(\w+)'ll\b", flags=re.I), r"\1 will"),
    (re.compile(r"\b(\w+)'s\b",  flags=re.I), r"\1 is"),   # simple heuristic
]


def normalise(txt: str) -> str:
    txt = unicodedata.normalize("NFC", txt)
    return re.sub(r"[ \t]{2,}", " ", txt).strip()

def expand_contractions(sentence: str) -> str:
    for pat, repl in CONTRACTIONS:
        sentence = pat.sub(repl, sentence)
    return sentence

def inject_name(sentence: str, name: str) -> str:
    """Ensure <name> appears (case‑insensitive). If no rule applies, return original."""
    if re.search(ENTITY_RE_TPL.format(re.escape(name)), sentence, flags=re.I):
        return sentence

    # Replace first 'they' or 'it'
    new, n = PRON_THEY_IT.subn(name, sentence, count=1)
    if n:
        return new

    # Replace token after 'this|these|those'
    def repl(m):
        return f"{m.group(1)} {name}"
    new, n = PRON_THIS_THESE.subn(repl, sentence, count=1)
    if n:
        return new

    return sentence  # keep unchanged if nothing matched


crea_f = OUT_CRE.open("w", encoding="utf-8")
item_f = OUT_ITEM.open("w", encoding="utf-8")

records = json.loads(SRC_JSON.read_text(encoding="utf-8"))

for rec in records:
    name = rec["name"].strip()
    cat  = rec["category"].lower()

    # split on "." and remove empty fragments
    for raw in filter(bool, (s.strip() for s in rec["description"].split("."))):
        sent = inject_name(normalise(raw) + ".", name)
        sent = expand_contractions(sent)

        if cat in CREA_CATS:
            crea_f.write(sent + "\n")
        elif cat in ITEM_CATS:
            item_f.write(sent + "\n")

crea_f.close(); item_f.close()
print("Finished:")
print(" •", OUT_CRE)
print(" •", OUT_ITEM)
