"""Recommendation history for variety across repeated prompts."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .normalization import normalize_terms


def build_input_key(vibe_text: str) -> str:
    return " ".join(normalize_terms(vibe_text))


def load_repeat_penalties(conn: Any, input_key: str) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT note_name, COUNT(*) AS count
        FROM recommendation_history
        WHERE input_key = %s
        GROUP BY note_name
        """,
        (input_key,),
    ).fetchall()
    counts = Counter({row["note_name"]: int(row["count"]) for row in rows})
    return {name: count * 10 for name, count in counts.items()}


def load_recent_note_names(conn: Any, input_key: str, limit: int = 5) -> list[str]:
    rows = conn.execute(
        """
        SELECT note_name
        FROM recommendation_history
        WHERE input_key = %s
        ORDER BY id DESC
        LIMIT %s
        """,
        (input_key, limit),
    ).fetchall()

    ordered: list[str] = []
    seen: set[str] = set()
    for row in rows:
        name = row["note_name"]
        if name in seen:
            continue
        seen.add(name)
        ordered.append(name)
    return ordered


def record_recommendations(conn: Any, input_key: str, note_names: list[str]) -> None:
    for note_name in note_names:
        conn.execute(
            """
            INSERT INTO recommendation_history (input_key, note_name)
            VALUES (%s, %s)
            """,
            (input_key, note_name),
        )
