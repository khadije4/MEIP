"""Header/text normalization utilities used by the ingestion mapper.

Rules (see docs/DATA_DICTIONARY.md "Column-header normalization rules"):
1. Unicode NFKD normalization + strip combining accents.
2. Lowercase.
3. Collapse repeated whitespace, trim.
4. Drop non-meaningful punctuation.
"""

from __future__ import annotations

import re
import unicodedata

_PUNCTUATION_RE = re.compile(r"[’'`,;:!?\"]")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(raw: str) -> str:
    if raw is None:
        return ""
    text = str(raw).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = _PUNCTUATION_RE.sub("", text)
    text = text.replace("(", " ").replace(")", " ")
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text
