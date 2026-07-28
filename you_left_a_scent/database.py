"""SQLite access helpers for the scent library."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .data import EMOTION_ALIASES, NOTE_SEEDS, category_for_tag


SEED_VERSION = 2


def default_db_path() -> Path:
    return Path(__file__).resolve().parent.parent / "you_left_a_scent.db"


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or default_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


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
            category TEXT NOT NULL DEFAULT 'emotion',
            PRIMARY KEY (input_term, tag_id),
            FOREIGN KEY (tag_id) REFERENCES vibe_tags(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS schema_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
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


def clear_seed_data(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DELETE FROM vibe_aliases;
        DELETE FROM note_vibe_tags;
        DELETE FROM vibe_tags;
        DELETE FROM notes;
        """
    )


def seed_database(conn: sqlite3.Connection) -> None:
    tag_ids: dict[str, int] = {}

    for note in NOTE_SEEDS:
        cur = conn.execute(
            """
            INSERT INTO notes (name, role, description, is_fallback)
            VALUES (?, ?, ?, ?)
            """,
            (note["name"], note["role"], note["description"], int(note.get("fallback", 0))),
        )
        note_id = cur.lastrowid

        for tag in note["tags"]:
            tag_id = tag_ids.get(tag)
            if tag_id is None:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO vibe_tags (tag, category) VALUES (?, ?)",
                    (tag, category_for_tag(tag)),
                )
                row = conn.execute("SELECT id FROM vibe_tags WHERE tag = ?", (tag,)).fetchone()
                tag_id = int(row["id"])
                tag_ids[tag] = tag_id

            conn.execute(
                "INSERT OR IGNORE INTO note_vibe_tags (note_id, tag_id, weight) VALUES (?, ?, ?)",
                (note_id, tag_id, _weight_for_tag(tag)),
            )

    seed_emotion_aliases(conn, tag_ids)
    conn.execute(
        """
        INSERT INTO schema_metadata (key, value)
        VALUES ('seed_version', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (str(SEED_VERSION),),
    )
    conn.commit()


def seed_emotion_aliases(conn: sqlite3.Connection, tag_ids: dict[str, int]) -> None:
    for input_term, target_tags in EMOTION_ALIASES.items():
        for target_tag in target_tags:
            tag_id = tag_ids.get(target_tag)
            if tag_id is None:
                conn.execute(
                    "INSERT OR IGNORE INTO vibe_tags (tag, category) VALUES (?, ?)",
                    (target_tag, category_for_tag(target_tag)),
                )
                row = conn.execute("SELECT id FROM vibe_tags WHERE tag = ?", (target_tag,)).fetchone()
                tag_id = int(row["id"])
                tag_ids[target_tag] = tag_id

            conn.execute(
                """
                INSERT OR IGNORE INTO vibe_aliases (input_term, tag_id, boost, category)
                VALUES (?, ?, ?, 'emotion')
                """,
                (input_term, tag_id, _boost_for_alias(input_term, target_tag)),
            )


def _boost_for_alias(input_term: str, target_tag: str) -> int:
    return 4 if input_term == target_tag else 2


def _weight_for_tag(tag: str) -> int:
    lowered = tag.lower()
    if lowered in {
        "romantic",
        "night out",
        "date night",
        "evening",
        "night",
        "sad",
        "melancholy",
        "lonely",
        "heartbroken",
        "grief",
        "hopeful",
        "joyful",
        "euphoric",
        "anxious",
        "angry",
        "sensual",
        "dreamy",
        "mysterious",
    }:
        return 3
    if lowered in {"clean", "fresh", "soft", "bright", "warm", "green", "luxury", "comforted", "vulnerable"}:
        return 2
    return 1


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
