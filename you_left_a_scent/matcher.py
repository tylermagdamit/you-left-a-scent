"""Deterministic scent matching without AI."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
import sqlite3


WORD_RE = re.compile(r"[a-z0-9']+")


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


def recommend(conn: sqlite3.Connection, vibe_text: str, limit: int = 4) -> tuple[list[ScentRecommendation], list[str]]:
    limit = max(3, min(5, int(limit)))
    terms = normalize_terms(vibe_text)
    if not terms:
        return [], []

    term_weights = {term: (3 if " " in term else 1) for term in terms}

    direct_rows = conn.execute(
        f"""
        SELECT id, tag
        FROM vibe_tags
        WHERE tag IN ({",".join("?" for _ in terms)})
        """,
        terms,
    ).fetchall()

    alias_rows = conn.execute(
        f"""
        SELECT vt.id, vt.tag, va.input_term, va.boost
        FROM vibe_aliases va
        JOIN vibe_tags vt ON vt.id = va.tag_id
        WHERE va.input_term IN ({",".join("?" for _ in terms)})
        """,
        terms,
    ).fetchall()

    matched_tag_weights: dict[int, int] = {}
    matched_tag_names: dict[int, str] = {}

    for row in direct_rows:
        tag_id = int(row["id"])
        matched_tag_names[tag_id] = row["tag"]
        matched_tag_weights[tag_id] = max(matched_tag_weights.get(tag_id, 0), term_weights.get(row["tag"], 1))

    for row in alias_rows:
        tag_id = int(row["id"])
        matched_tag_names[tag_id] = row["tag"]
        matched_tag_weights[tag_id] = max(matched_tag_weights.get(tag_id, 0), int(row["boost"]))

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
        key=lambda item: (-item[0], item[1]),
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
