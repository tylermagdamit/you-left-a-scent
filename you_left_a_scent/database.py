"""Backward-compatible PostgreSQL database helpers."""

from __future__ import annotations

from typing import Any, Iterable

from .db import connect, initialize


def query_matching_notes(conn: Any, terms: Iterable[str]) -> list[dict[str, Any]]:
    values = list(terms)
    if not values:
        return []
    return conn.execute(
        """SELECT DISTINCT n.name, n.role, n.description FROM notes n
           JOIN note_vibe_tags nvt ON nvt.note_id = n.id
           JOIN vibe_tags vt ON vt.id = nvt.tag_id WHERE vt.tag = ANY(%s)""",
        (values,),
    ).fetchall()


__all__ = ["connect", "initialize", "query_matching_notes"]
