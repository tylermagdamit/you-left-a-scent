"""Command-line interface for You Left a Scent."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .database import connect, default_db_path, initialize
from .matcher import recommend


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="you left a scent",
        description="Turn a short vibe sentence into 3 to 5 scent notes using a local SQLite database.",
    )
    parser.add_argument("vibe", nargs="*", help='A short phrase like "robotic sunrise" or "romantic night out".')
    parser.add_argument("-n", "--count", type=int, default=4, help="How many notes to return, between 3 and 5.")
    parser.add_argument("--db", type=Path, default=default_db_path(), help="Path to the SQLite database file.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    vibe_text = " ".join(args.vibe).strip()
    if not vibe_text:
        vibe_text = input("Describe the vibe in a short sentence: ").strip()

    with connect(args.db) as conn:
        initialize(conn)
        notes, matched_tags = recommend(conn, vibe_text, limit=args.count)

    print("\nYou Left a Scent")
    print("=" * 16)
    print(f"Vibe: {vibe_text}")
    if matched_tags:
        print(f"Matched tags: {', '.join(matched_tags[:8])}")
    else:
        print("Matched tags: none, using fallback scent anchors")
    print()

    for index, note in enumerate(notes, start=1):
        print(f"{index}. {note.name} [{note.role}]")
        print(f"   {note.description}")
        if note.matched_tags:
            print(f"   Why it fits: {', '.join(note.matched_tags)}")
        print()

    return 0

