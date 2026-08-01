"""Cleans raw source row labels (non-breaking-space indentation + numbering
prefixes like "1.", "1. 1", "2.2.", "2. 2.1") into a clean display string,
while the caller keeps the raw text verbatim as `original_label` for
provenance."""

from __future__ import annotations

import re

_NUMBERING_PREFIX_RE = re.compile(r"^[\d]+(\.[\d]*)*\.?\s*(\d+(\.\d+)?)?\s*")
_WHITESPACE_RE = re.compile(r"\s+")


def clean_label(raw: str) -> str:
    if raw is None:
        return ""
    text = str(raw).replace("\xa0", " ")
    text = text.strip()
    # Strip a leading numbering token, e.g. "1.", "1. 1", "2.2.", "2. 2.1",
    # "10.". Applied once; source numbering is always a single prefix token.
    stripped = _NUMBERING_PREFIX_RE.sub("", text, count=1).strip()
    if stripped:
        text = stripped
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text
