"""Backward-compatible database imports."""

from __future__ import annotations

import sqlite3
from typing import Iterable

from .db import connect, default_db_path, initialize


def query_matching_notes(conn: sqlite3.Connection, terms: Iterable[str]) -> list[sqlite3.Row]:
    terms = [term for term in terms if term]
    if not terms:
        return []

    placeholders = ",".join("?" for _ in terms)
    return list(
        conn.execute(
            f"""
            SELECT DISTINCT n.id, n.name, n.role, n.description
            FROM notes n
            JOIN note_vibe_tags nvt ON nvt.note_id = n.id
            JOIN vibe_tags vt ON vt.id = nvt.tag_id
            WHERE vt.tag IN ({placeholders})
            ORDER BY n.name
            """,
            terms,
        )
    )
