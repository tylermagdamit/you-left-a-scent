"""PostgreSQL connection helpers."""

from __future__ import annotations

import os
from typing import Any

import psycopg
from psycopg.rows import dict_row


def connect(database_url: str | None = None) -> psycopg.Connection[dict[str, Any]]:
    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required. Set it to your PostgreSQL connection URL.")
    return psycopg.connect(url, row_factory=dict_row)

