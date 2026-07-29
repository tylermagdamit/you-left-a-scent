"""Application service that adapts the matcher for HTTP responses."""

from dataclasses import asdict

from ..db import connect, initialize
from ..matching import recommend, visual_direction


def recommend_for_web(vibe: str, count: int) -> dict[str, object]:
    with connect() as conn:
        initialize(conn)
        notes, matched_tags = recommend(conn, vibe, limit=count)

    return {
        "vibe": vibe,
        "matched_tags": matched_tags,
        "theme": asdict(visual_direction(matched_tags, notes)),
        "notes": [
            {
                "name": note.name,
                "role": note.role,
                "description": note.description,
                "score": note.score,
                "matched_tags": list(note.matched_tags),
            }
            for note in notes
        ],
    }
