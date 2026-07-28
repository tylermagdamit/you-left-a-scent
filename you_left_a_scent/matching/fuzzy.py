"""RapidFuzz-backed local tag matching."""

from __future__ import annotations

try:
    from rapidfuzz import fuzz, process
except ImportError:  # pragma: no cover - depends on the local environment.
    fuzz = None
    process = None


FUZZY_SCORE_CUTOFF = 78
MIN_TERM_LENGTH = 4


def fuzzy_matches(
    terms: list[str],
    choices: list[str],
    limit: int = 3,
    excluded_terms: set[str] | None = None,
) -> list[tuple[str, int, str]]:
    _require_rapidfuzz()

    excluded_terms = excluded_terms or set()
    matches: list[tuple[str, int, str]] = []
    for term in terms:
        if term in excluded_terms:
            continue
        # Skip very short terms to avoid false positives (e.g. "man" → "mandarin")
        if len(term) < MIN_TERM_LENGTH:
            continue
        term_word_count = len(term.split())
        for choice, score, _ in process.extract(
            term,
            choices,
            scorer=fuzz.WRatio,
            score_cutoff=FUZZY_SCORE_CUTOFF,
            limit=limit,
        ):
            if choice == term:
                continue
            if len(choice.split()) != term_word_count:
                continue
            # Apply substring penalty: if term is a substring of choice, raise the bar
            if term in choice and len(term) < len(choice):
                if score < 92:
                    continue
            matches.append((choice, int(score), term))
    return matches


def weight_from_fuzzy_score(score: int, input_term: str) -> int:
    phrase_bonus = 1 if " " in input_term else 0
    if score >= 96:
        return 3 + phrase_bonus
    if score >= 90:
        return 2 + phrase_bonus
    return 2 + phrase_bonus


def _require_rapidfuzz() -> None:
    if fuzz is None or process is None:
        raise RuntimeError(
            "rapidfuzz is required for fuzzy matching. Install it with: pip install -r requirements.txt"
        )

