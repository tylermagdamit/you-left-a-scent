"""SQLite connection helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def default_db_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "you_left_a_scent.db"


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or default_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

