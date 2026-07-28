"""Backward-compatible matching imports."""

from __future__ import annotations

from .matching import ScentRecommendation, normalize_terms, recommend

__all__ = ["ScentRecommendation", "normalize_terms", "recommend"]
