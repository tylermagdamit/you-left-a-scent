"""Deterministic scent matching without AI."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
import sqlite3

try:
    from rapidfuzz import fuzz, process
except ImportError:  # pragma: no cover - depends on the local environment.
    fuzz = None
    process = None


WORD_RE = re.compile(r"[a-z0-9']+")
FUZZY_SCORE_CUTOFF = 78


@dataclass(frozen=True)
class ScentRecommendation:
    name: str
    role: str
    description: str
    score: int
    matched_tags: tuple[str, ...]


def normalize_terms(text: str) -> list[str]:
    raw_terms = WORD_RE.findall(text.lower())
    phrases = [" ".join(raw_terms[i : i + 2]) for i in range(len(raw_terms) - 1)]
    return list(dict.fromkeys(raw_terms + phrases))


def _require_rapidfuzz() -> None:
    if fuzz is None or process is None:
        raise RuntimeError(
            "rapidfuzz is required for fuzzy matching. Install it with: pip install -r requirements.txt"
        )


def _load_match_choices(conn: sqlite3.Connection) -> tuple[dict[str, tuple[int, str]], dict[str, list[sqlite3.Row]]]:
    tag_rows = conn.execute("SELECT id, tag, category FROM vibe_tags").fetchall()
    alias_rows = conn.execute(
        """
        SELECT va.input_term, va.boost, vt.id, vt.tag
        FROM vibe_aliases va
        JOIN vibe_tags vt ON vt.id = va.tag_id
        """
    ).fetchall()

    direct_choices = {row["tag"]: (int(row["id"]), row["category"]) for row in tag_rows}
    alias_choices: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in alias_rows:
        alias_choices[row["input_term"]].append(row)

    return direct_choices, alias_choices


def _fuzzy_matches(
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
            matches.append((choice, int(score), term))
    return matches


def recommend(conn: sqlite3.Connection, vibe_text: str, limit: int = 4) -> tuple[list[ScentRecommendation], list[str]]:
    limit = max(3, min(5, int(limit)))
    terms = normalize_terms(vibe_text)
    if not terms:
        return [], []

    term_weights = {term: (4 if " " in term else 3) for term in terms}
    direct_choices, alias_choices = _load_match_choices(conn)
    exact_terms: set[str] = set()

    direct_rows = conn.execute(
        f"""
        SELECT id, tag, category
        FROM vibe_tags
        WHERE tag IN ({",".join("?" for _ in terms)})
        """,
        terms,
    ).fetchall()
    exact_terms.update(row["tag"] for row in direct_rows)

    alias_rows = conn.execute(
        f"""
        SELECT vt.id, vt.tag, va.input_term, va.boost
        FROM vibe_aliases va
        JOIN vibe_tags vt ON vt.id = va.tag_id
        WHERE va.input_term IN ({",".join("?" for _ in terms)})
        """,
        terms,
    ).fetchall()
    exact_terms.update(row["input_term"] for row in alias_rows)

    matched_tag_weights: dict[int, int] = {}
    matched_tag_names: dict[int, str] = {}
    fuzzy_source_terms: dict[str, set[str]] = defaultdict(set)
    concrete_tag_names: set[str] = set()

    for row in direct_rows:
        tag_id = int(row["id"])
        matched_tag_names[tag_id] = row["tag"]
        matched_tag_weights[tag_id] = max(matched_tag_weights.get(tag_id, 0), term_weights.get(row["tag"], 1))
        if row["category"] != "emotion":
            concrete_tag_names.add(row["tag"])

    for row in alias_rows:
        tag_id = int(row["id"])
        matched_tag_names[tag_id] = row["tag"]
        matched_tag_weights[tag_id] = max(matched_tag_weights.get(tag_id, 0), int(row["boost"]))

    tag_choices = list(direct_choices)
    for matched_choice, score, input_term in _fuzzy_matches(terms, tag_choices, excluded_terms=exact_terms):
        tag_id, category = direct_choices[matched_choice]
        matched_tag_names[tag_id] = matched_choice
        matched_tag_weights[tag_id] = max(matched_tag_weights.get(tag_id, 0), _weight_from_fuzzy_score(score, input_term))
        fuzzy_source_terms[matched_choice].add(input_term)
        if category != "emotion":
            concrete_tag_names.add(matched_choice)

    for matched_alias, score, input_term in _fuzzy_matches(terms, list(alias_choices), excluded_terms=exact_terms):
        for row in alias_choices[matched_alias]:
            tag_id = int(row["id"])
            matched_tag_names[tag_id] = row["tag"]
            boost = max(1, int(row["boost"]) - 1) + _weight_from_fuzzy_score(score, input_term)
            matched_tag_weights[tag_id] = max(matched_tag_weights.get(tag_id, 0), boost)
            fuzzy_source_terms[row["tag"]].add(input_term)

    matched_tags = list(dict.fromkeys(matched_tag_names.values()))
    matched_weights_by_name = {
        matched_tag_names[tag_id]: weight
        for tag_id, weight in matched_tag_weights.items()
    }
    if not matched_tag_weights:
        fallback_rows = conn.execute(
            """
            SELECT name, role, description
            FROM notes
            WHERE is_fallback = 1
            ORDER BY name
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return (
            [
                ScentRecommendation(
                    name=row["name"],
                    role=row["role"],
                    description=row["description"],
                    score=0,
                    matched_tags=(),
                )
                for row in fallback_rows
            ],
            matched_tags,
        )

    scores: dict[int, int] = defaultdict(int)
    evidence: dict[int, set[str]] = defaultdict(set)
    note_meta: dict[int, tuple[str, str, str]] = {}

    placeholders = ",".join("?" for _ in matched_tag_weights)
    scored_rows = conn.execute(
        f"""
        SELECT n.id, n.name, n.role, n.description, vt.tag, nvt.weight
        FROM note_vibe_tags nvt
        JOIN notes n ON n.id = nvt.note_id
        JOIN vibe_tags vt ON vt.id = nvt.tag_id
        WHERE nvt.tag_id IN ({placeholders})
        """,
        tuple(matched_tag_weights),
    ).fetchall()

    for row in scored_rows:
        note_id = int(row["id"])
        note_meta[note_id] = (row["name"], row["role"], row["description"])
        tag_boost = matched_weights_by_name.get(row["tag"], 1)
        scores[note_id] += int(row["weight"]) * tag_boost
        evidence[note_id].add(row["tag"])
        for input_term in fuzzy_source_terms[row["tag"]]:
            evidence[note_id].add(f"{input_term} ~= {row['tag']}")

    ranked = sorted(
        (
            (
                score,
                note_meta[note_id][0],
                note_meta[note_id][1],
                note_meta[note_id][2],
                tuple(sorted(evidence[note_id])),
            )
            for note_id, score in scores.items()
        ),
        key=lambda item: (-item[0], -len(item[4]), item[1]),
    )

    unique: list[ScentRecommendation] = []
    seen: set[str] = set()
    for score, name, role, description, tags in ranked:
        if name in seen:
            continue
        seen.add(name)
        unique.append(
            ScentRecommendation(
                name=name,
                role=role,
                description=description,
                score=score,
                matched_tags=tags,
            )
        )
        if len(unique) >= limit:
            break

    _represent_concrete_tags(unique, ranked, concrete_tag_names, limit)

    if len(unique) < limit:
        remaining_rows = conn.execute(
            """
            SELECT name, role, description
            FROM notes
            WHERE name NOT IN ({})
            ORDER BY is_fallback DESC, name
            LIMIT ?
            """.format(",".join("?" for _ in seen) if seen else "''"),
            tuple(seen) + (limit - len(unique),) if seen else (limit - len(unique),),
        ).fetchall()
        for row in remaining_rows:
            unique.append(
                ScentRecommendation(
                    name=row["name"],
                    role=row["role"],
                    description=row["description"],
                    score=0,
                    matched_tags=(),
                )
            )

    return unique[:limit], matched_tags


def _represent_concrete_tags(
    recommendations: list[ScentRecommendation],
    ranked: list[tuple[int, str, str, str, tuple[str, ...]]],
    concrete_tag_names: set[str],
    limit: int,
) -> None:
    for tag in concrete_tag_names:
        if any(tag in note.matched_tags for note in recommendations):
            continue

        replacement = next((item for item in ranked if tag in item[4]), None)
        if replacement is None:
            continue

        score, name, role, description, tags = replacement
        if any(note.name == name for note in recommendations):
            continue

        new_note = ScentRecommendation(
            name=name,
            role=role,
            description=description,
            score=score,
            matched_tags=tags,
        )
        if len(recommendations) < limit:
            recommendations.append(new_note)
        else:
            recommendations[-1] = new_note


def _weight_from_fuzzy_score(score: int, input_term: str) -> int:
    phrase_bonus = 1 if " " in input_term else 0
    if score >= 96:
        return 3 + phrase_bonus
    if score >= 90:
        return 2 + phrase_bonus
    return 2 + phrase_bonus
