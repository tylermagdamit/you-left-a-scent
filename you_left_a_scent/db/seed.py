"""Database seeding for notes, tags, and aliases."""

from __future__ import annotations

import sqlite3

from you_left_a_scent.catalog import NOTE_SEEDS, VIBE_ALIASES, category_for_tag


SEED_VERSION = 12


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

        for tag in [str(note["name"]).lower(), *note["tags"]]:
            tag_id = _ensure_tag(conn, tag_ids, tag)
            conn.execute(
                "INSERT OR IGNORE INTO note_vibe_tags (note_id, tag_id, weight) VALUES (?, ?, ?)",
                (note_id, tag_id, _weight_for_tag(tag)),
            )

    seed_vibe_aliases(conn, tag_ids)
    conn.execute(
        """
        INSERT INTO schema_metadata (key, value)
        VALUES ('seed_version', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (str(SEED_VERSION),),
    )
    conn.commit()


def seed_vibe_aliases(conn: sqlite3.Connection, tag_ids: dict[str, int]) -> None:
    for input_term, target_tags in VIBE_ALIASES.items():
        for target_tag in target_tags:
            tag_id = _ensure_tag(conn, tag_ids, target_tag)
            conn.execute(
                """
                INSERT OR IGNORE INTO vibe_aliases (input_term, tag_id, boost, category)
                VALUES (?, ?, ?, 'vibe')
                """,
                (input_term, tag_id, _boost_for_alias(input_term, target_tag)),
            )


def _ensure_tag(conn: sqlite3.Connection, tag_ids: dict[str, int], tag: str) -> int:
    tag_id = tag_ids.get(tag)
    if tag_id is not None:
        return tag_id

    conn.execute(
        "INSERT OR IGNORE INTO vibe_tags (tag, category) VALUES (?, ?)",
        (tag, category_for_tag(tag)),
    )
    row = conn.execute("SELECT id FROM vibe_tags WHERE tag = ?", (tag,)).fetchone()
    tag_id = int(row["id"])
    tag_ids[tag] = tag_id
    return tag_id


def _boost_for_alias(input_term: str, target_tag: str) -> int:
    if " " in input_term:
        return 3
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
        "jealous",
        "homesick",
        "embarrassed",
        "curious",
        "focused",
        "burned out",
        "overwhelmed",
        "in love",
        "homesafe",
    }:
        return 3
    if lowered in {"clean", "fresh", "soft", "bright", "warm", "green", "luxury", "comforted", "vulnerable"}:
        return 2
    return 1
