"""Numeric parsing tolerant of French formatting (comma decimals, spaces /
non-breaking spaces as thousands separators) without ever guessing a value
for genuinely non-numeric text."""

from __future__ import annotations

import re

_THOUSANDS_RE = re.compile(r"[\s  ]")


class NotNumericError(ValueError):
    pass


def parse_numeric(raw: str) -> float:
    text = raw.strip()
    if text == "":
        raise NotNumericError("empty")
    cleaned = _THOUSANDS_RE.sub("", text)
    # French decimal comma: only treat comma as decimal separator when there
    # is no dot already present (avoids mangling "1.234,56" edge cases by
    # instead just failing them as non-numeric, which is the safe choice).
    if "," in cleaned and "." not in cleaned:
        cleaned = cleaned.replace(",", ".")
    elif "," in cleaned and "." in cleaned:
        raise NotNumericError(f"ambiguous numeric format: {raw!r}")
    try:
        return float(cleaned)
    except ValueError as exc:
        raise NotNumericError(str(exc)) from exc
