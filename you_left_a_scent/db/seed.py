"""PostgreSQL seeding for notes, tags, and aliases."""

from __future__ import annotations

from typing import Any

from you_left_a_scent.catalog import NOTE_SEEDS, VIBE_ALIASES, category_for_tag


SEED_VERSION = 32


def clear_seed_data(conn: Any) -> None:
    conn.execute("DELETE FROM vibe_aliases")
    conn.execute("DELETE FROM note_vibe_tags")
    conn.execute("DELETE FROM vibe_tags")
    conn.execute("DELETE FROM notes")


def seed_database(conn: Any) -> None:
    tag_ids: dict[str, int] = {}
    for note in NOTE_SEEDS:
        note_id = conn.execute(
            """INSERT INTO notes (name, role, description, is_fallback)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (note["name"], note["role"], note["description"], bool(note.get("fallback", 0))),
        ).fetchone()["id"]
        for tag in [str(note["name"]).lower(), *note["tags"]]:
            tag_id = _ensure_tag(conn, tag_ids, tag)
            conn.execute(
                """INSERT INTO note_vibe_tags (note_id, tag_id, weight) VALUES (%s, %s, %s)
                   ON CONFLICT (note_id, tag_id) DO NOTHING""",
                (note_id, tag_id, _weight_for_tag(tag)),
            )
    seed_vibe_aliases(conn, tag_ids)
    conn.execute(
        """INSERT INTO schema_metadata (key, value) VALUES ('seed_version', %s)
           ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value""",
        (str(SEED_VERSION),),
    )


def seed_vibe_aliases(conn: Any, tag_ids: dict[str, int]) -> None:
    for input_term, target_tags in VIBE_ALIASES.items():
        for target_tag in target_tags:
            tag_id = _ensure_tag(conn, tag_ids, target_tag)
            conn.execute(
                """INSERT INTO vibe_aliases (input_term, tag_id, boost, category)
                   VALUES (%s, %s, %s, 'vibe') ON CONFLICT (input_term, tag_id) DO NOTHING""",
                (input_term, tag_id, _boost_for_alias(input_term, target_tag)),
            )


def _ensure_tag(conn: Any, tag_ids: dict[str, int], tag: str) -> int:
    if tag in tag_ids:
        return tag_ids[tag]
    row = conn.execute(
        """INSERT INTO vibe_tags (tag, category) VALUES (%s, %s)
           ON CONFLICT (tag) DO UPDATE SET tag = EXCLUDED.tag RETURNING id""",
        (tag, category_for_tag(tag)),
    ).fetchone()
    tag_ids[tag] = int(row["id"])
    return tag_ids[tag]


def _boost_for_alias(input_term: str, target_tag: str) -> int:
    return 3 if " " in input_term else (4 if input_term == target_tag else 2)


def _weight_for_tag(tag: str) -> int:
    lowered = tag.lower()
    if lowered in {
        "romantic", "night out", "date night", "evening", "night", "sad", "melancholy", "lonely",
        "heartbroken", "grief", "hopeful", "joyful", "euphoric", "anxious", "angry", "sensual",
        "dreamy", "mysterious", "jealous", "homesick", "embarrassed", "curious", "focused",
        "burned out", "overwhelmed", "in love", "homesafe", "intense", "longing", "excited",
        "cozy", "reflective", "melancholic", "energetic", "meditative", "nostalgic", "bittersweet",
        "tension", "hopeless", "desperate", "ashamed", "grateful", "tender", "playful", "content",
        "serene", "wistful", "peaceful", "confident", "restless", "vulnerable", "comforted",
    }:
        return 3
    if lowered in {
        "clean", "fresh", "soft", "bright", "warm", "green", "luxury", "dry", "sweet", "spicy",
        "smoky", "earthy", "woody", "floral", "powdery", "creamy", "smooth", "golden", "silver",
        "dark", "cool", "cold", "airy", "light", "rich", "bold", "muted", "quiet", "calm",
        "minimal", "polished", "sunlit", "fresh air",
    }:
        return 2
    return 1
