"""Backward-compatible access to catalog seed data."""

from __future__ import annotations

from .catalog import NOTE_SEEDS, TAG_CATEGORIES, VIBE_ALIASES, category_for_tag

__all__ = ["NOTE_SEEDS", "TAG_CATEGORIES", "VIBE_ALIASES", "category_for_tag"]
