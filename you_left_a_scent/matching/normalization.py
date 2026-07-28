"""Input normalization for vibe text."""

from __future__ import annotations

import re


WORD_RE = re.compile(r"[a-z0-9']+")


def normalize_terms(text: str) -> list[str]:
    raw_terms = WORD_RE.findall(text.lower())
    phrases = [" ".join(raw_terms[i : i + 2]) for i in range(len(raw_terms) - 1)]
    return list(dict.fromkeys(raw_terms + phrases))

