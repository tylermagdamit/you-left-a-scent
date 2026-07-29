"""PostgreSQL schema creation and seed-version checks."""

from __future__ import annotations

from typing import Any

from .seed import SEED_VERSION, clear_seed_data, seed_database


_SCHEMA = (
    """CREATE TABLE IF NOT EXISTS notes (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name TEXT NOT NULL UNIQUE, role TEXT NOT NULL, description TEXT NOT NULL,
        is_fallback BOOLEAN NOT NULL DEFAULT FALSE)""",
    """CREATE TABLE IF NOT EXISTS vibe_tags (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        tag TEXT NOT NULL UNIQUE, category TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS note_vibe_tags (
        note_id BIGINT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
        tag_id BIGINT NOT NULL REFERENCES vibe_tags(id) ON DELETE CASCADE,
        weight INTEGER NOT NULL DEFAULT 1, PRIMARY KEY (note_id, tag_id))""",
    """CREATE TABLE IF NOT EXISTS vibe_aliases (
        input_term TEXT NOT NULL, tag_id BIGINT NOT NULL REFERENCES vibe_tags(id) ON DELETE CASCADE,
        boost INTEGER NOT NULL DEFAULT 1, category TEXT NOT NULL DEFAULT 'vibe',
        PRIMARY KEY (input_term, tag_id))""",
    "CREATE TABLE IF NOT EXISTS schema_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
    """CREATE TABLE IF NOT EXISTS recommendation_history (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, input_key TEXT NOT NULL,
        note_name TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)""",
)


def initialize(conn: Any) -> None:
    for statement in _SCHEMA:
        conn.execute(statement)

    count = conn.execute("SELECT COUNT(*) AS count FROM notes").fetchone()["count"]
    seed_version = conn.execute(
        "SELECT value FROM schema_metadata WHERE key = 'seed_version'"
    ).fetchone()
    if count == 0 or seed_version is None or int(seed_version["value"]) < SEED_VERSION:
        clear_seed_data(conn)
        seed_database(conn)
    conn.commit()
