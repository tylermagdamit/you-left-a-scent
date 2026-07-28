"""SQLite queries used by the matching engine."""

from __future__ import annotations

from collections import defaultdict
import sqlite3


def load_match_choices(conn: sqlite3.Connection) -> tuple[dict[str, tuple[int, str]], dict[str, list[sqlite3.Row]]]:
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


def load_fallback_notes(conn: sqlite3.Connection, limit: int) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT name, role, description
        FROM notes
        WHERE is_fallback = 1
        ORDER BY name
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

