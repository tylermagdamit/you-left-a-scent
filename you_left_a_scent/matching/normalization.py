"""Input normalization for vibe text."""

from __future__ import annotations

import re

from ..catalog.syntax import SENTENCE_FILLER_WORDS


WORD_RE = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")


def normalize_terms(text: str) -> list[str]:
    raw_terms = [term for term in WORD_RE.findall(text.lower()) if term not in SENTENCE_FILLER_WORDS]
    chunks: list[list[str]] = []
    current_chunk: list[str] = []

    for term in WORD_RE.findall(text.lower()):
        if term in SENTENCE_FILLER_WORDS:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
            continue
        current_chunk.append(term)

    if current_chunk:
        chunks.append(current_chunk)

    phrases = [" ".join(chunk[i : i + 2]) for chunk in chunks for i in range(len(chunk) - 1)]
    return list(dict.fromkeys(raw_terms + phrases))
