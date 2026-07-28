"""Combined alias catalog for abstract vibe matching."""

from __future__ import annotations

from .aesthetics import AESTHETIC_ALIASES
from .adjectives import ADJECTIVE_ALIASES
from .colors import COLOR_ALIASES
from .events import EVENT_ALIASES
from .emotions import EMOTION_ALIASES
from .expressions import EXPRESSION_ALIASES
from .food_and_drinks import FOOD_AND_DRINK_ALIASES
from .places import PLACE_ALIASES
from .scenarios import SCENARIO_ALIASES
from .seasons import SEASON_ALIASES


VIBE_ALIASES = {
    **PLACE_ALIASES,
    **SCENARIO_ALIASES,
    **SEASON_ALIASES,
    **COLOR_ALIASES,
    **EVENT_ALIASES,
    **EMOTION_ALIASES,
    **EXPRESSION_ALIASES,
    **ADJECTIVE_ALIASES,
    **AESTHETIC_ALIASES,
    **FOOD_AND_DRINK_ALIASES,
}

__all__ = ["VIBE_ALIASES"]
