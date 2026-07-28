"""Shared matching data models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScentRecommendation:
    name: str
    role: str
    description: str
    score: int
    matched_tags: tuple[str, ...]

