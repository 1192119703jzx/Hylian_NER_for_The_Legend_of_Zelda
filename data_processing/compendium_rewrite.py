
"""
Expand ’re → are, ’s → is, ’ve → have, ’ll → will
in the CREA and ITEM synthetic sentence files.

Usage:
    python expand_contractions.py
"""

import re
from pathlib import Path

FILES = ["synthetic_crea.txt", "synthetic_item.txt"]

CONTRACTIONS = [
    (re.compile(r"\b(\w+)'re\b", flags=re.I), r"\1 are"),
    (re.compile(r"\b(\w+)'ve\b", flags=re.I), r"\1 have"),
    (re.compile(r"\b(\w+)'ll\b", flags=re.I), r"\1 will"),
    (re.compile(r"\b(\w+)'s\b",  flags=re.I), r"\1 is"),   # simple ’s → is
]

def expand(line: str) -> str:
    for pat, repl in CONTRACTIONS:
        line = pat.sub(repl, line)
    return line

def process(path: Path) -> None:
    out_path = path.with_stem(path.stem + "_expanded")
    with path.open(encoding="utf-8") as src, out_path.open("w", encoding="utf-8") as dst:
        for raw in src:
            dst.write(expand(raw.rstrip()) + "\n")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    for fname in FILES:
        p = Path(fname)
        if p.exists():
            process(p)
        else:
            print(f"Warning: {fname} not found")
