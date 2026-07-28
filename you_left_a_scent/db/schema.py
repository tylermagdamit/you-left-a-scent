"""SQLite schema creation and seed-version checks."""

from __future__ import annotations

import sqlite3

from .seed import SEED_VERSION, clear_seed_data, seed_database


def initialize(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            description TEXT NOT NULL,
            is_fallback INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS vibe_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS note_vibe_tags (
            note_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            weight INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (note_id, tag_id),
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES vibe_tags(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS vibe_aliases (
            input_term TEXT NOT NULL,
            tag_id INTEGER NOT NULL,
            boost INTEGER NOT NULL DEFAULT 1,
            category TEXT NOT NULL DEFAULT 'vibe',
            PRIMARY KEY (input_term, tag_id),
            FOREIGN KEY (tag_id) REFERENCES vibe_tags(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS schema_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recommendation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_key TEXT NOT NULL,
            note_name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    seed_version = conn.execute(
        "SELECT value FROM schema_metadata WHERE key = 'seed_version'"
    ).fetchone()

    if count == 0 or seed_version is None or int(seed_version["value"]) < SEED_VERSION:
        clear_seed_data(conn)
        seed_database(conn)
