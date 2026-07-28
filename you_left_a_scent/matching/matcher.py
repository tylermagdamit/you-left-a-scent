"""Deterministic scent matching without AI."""

from __future__ import annotations

from collections import defaultdict
import sqlite3

from .fuzzy import fuzzy_matches, weight_from_fuzzy_score
from .history import build_input_key, load_recent_note_names, load_repeat_penalties, record_recommendations
from .models import ScentRecommendation
from .normalization import normalize_terms
from .repository import load_fallback_notes, load_match_choices


def recommend(conn: sqlite3.Connection, vibe_text: str, limit: int = 4) -> tuple[list[ScentRecommendation], list[str]]:
    limit = max(3, min(5, int(limit)))
    terms = normalize_terms(vibe_text)
    if not terms:
        return [], []
    input_key = build_input_key(vibe_text)

    term_weights = {term: (4 if " " in term else 3) for term in terms}
    direct_choices, alias_choices = load_match_choices(conn)
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

    for matched_choice, score, input_term in fuzzy_matches(
        terms,
        list(direct_choices),
        excluded_terms=exact_terms,
    ):
        tag_id, category = direct_choices[matched_choice]
        matched_tag_names[tag_id] = matched_choice
        matched_tag_weights[tag_id] = max(
            matched_tag_weights.get(tag_id, 0),
            weight_from_fuzzy_score(score, input_term),
        )
        fuzzy_source_terms[matched_choice].add(input_term)
        if category != "emotion":
            concrete_tag_names.add(matched_choice)

    for matched_alias, score, input_term in fuzzy_matches(
        terms,
        list(alias_choices),
        excluded_terms=exact_terms,
    ):
        for row in alias_choices[matched_alias]:
            tag_id = int(row["id"])
            matched_tag_names[tag_id] = row["tag"]
            boost = max(1, int(row["boost"]) - 1) + weight_from_fuzzy_score(score, input_term)
            matched_tag_weights[tag_id] = max(matched_tag_weights.get(tag_id, 0), boost)
            fuzzy_source_terms[row["tag"]].add(input_term)

    matched_tags = list(dict.fromkeys(matched_tag_names.values()))
    matched_weights_by_name = {
        matched_tag_names[tag_id]: weight
        for tag_id, weight in matched_tag_weights.items()
    }
    if not matched_tag_weights:
        notes = _fallback_recommendations(conn, limit)
        record_recommendations(conn, input_key, [note.name for note in notes])
        conn.commit()
        return notes, matched_tags

    repeat_penalties = load_repeat_penalties(conn, input_key)
    ranked = _rank_notes(
        conn,
        matched_tag_weights,
        matched_weights_by_name,
        fuzzy_source_terms,
        repeat_penalties,
    )

    recent_note_names = load_recent_note_names(conn, input_key, limit=limit)
    unique: list[ScentRecommendation] = []
    seen: set[str] = set()
    selection_pool = [item for item in ranked if item[1] not in recent_note_names]
    if len(selection_pool) < limit:
        selection_pool.extend(item for item in ranked if item[1] in recent_note_names)

    for score, name, role, description, tags in selection_pool:
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
    _fill_short_result(conn, unique, seen, limit)
    record_recommendations(conn, input_key, [note.name for note in unique[:limit]])
    conn.commit()
    return unique[:limit], matched_tags


def _fallback_recommendations(conn: sqlite3.Connection, limit: int) -> list[ScentRecommendation]:
    return [
        ScentRecommendation(
            name=row["name"],
            role=row["role"],
            description=row["description"],
            score=0,
            matched_tags=(),
        )
        for row in load_fallback_notes(conn, limit)
    ]


def _rank_notes(
    conn: sqlite3.Connection,
    matched_tag_weights: dict[int, int],
    matched_weights_by_name: dict[str, int],
    fuzzy_source_terms: dict[str, set[str]],
    repeat_penalties: dict[str, int],
) -> list[tuple[int, str, str, str, tuple[str, ...]]]:
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

    return sorted(
        (
            (
                score - repeat_penalties.get(note_meta[note_id][0], 0),
                note_meta[note_id][0],
                note_meta[note_id][1],
                note_meta[note_id][2],
                tuple(sorted(evidence[note_id])),
            )
            for note_id, score in scores.items()
        ),
        key=lambda item: (-item[0], -len(item[4]), item[1]),
    )


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


def _fill_short_result(
    conn: sqlite3.Connection,
    recommendations: list[ScentRecommendation],
    seen: set[str],
    limit: int,
) -> None:
    if len(recommendations) >= limit:
        return

    placeholders = ",".join("?" for _ in seen) if seen else "''"
    remaining_rows = conn.execute(
        f"""
        SELECT name, role, description
        FROM notes
        WHERE name NOT IN ({placeholders})
        ORDER BY is_fallback DESC, name
        LIMIT ?
        """,
        tuple(seen) + (limit - len(recommendations),) if seen else (limit - len(recommendations),),
    ).fetchall()
    for row in remaining_rows:
        recommendations.append(
            ScentRecommendation(
                name=row["name"],
                role=row["role"],
                description=row["description"],
                score=0,
                matched_tags=(),
            )
        )
