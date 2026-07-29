"""GUI-ready visual families derived from matched tags and scent notes."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import ScentRecommendation


@dataclass(frozen=True)
class VisualDirection:
    """Palette plus the returned scent notes to place in visual GUI layers."""

    name: str
    background: str
    surface: str
    accent: str
    text: str
    glow: str
    note_layers: tuple[tuple[str, str], ...] = ()


_THEMES: tuple[tuple[VisualDirection, frozenset[str]], ...] = (
    (VisualDirection("sunlit", "#FFF8D8", "#FFFDF2", "#F6C945", "#493B16", "#FFE58A"), frozenset({"happy", "joyful", "hopeful", "bright", "sparkling", "citrus", "sunrise", "daylight", "sunlit", "yellow", "gold", "golden", "energetic", "playful", "excited"})),
    (VisualDirection("blush", "#FFF0F3", "#FFFAFB", "#E78AA4", "#542D3B", "#FFC5D4"), frozenset({"romantic", "in love", "tender", "flirty", "sensual", "rose", "peony", "pink", "blush", "soft", "skin", "velvet"})),
    (VisualDirection("stillness", "#EEF7F3", "#FAFFFC", "#78BFA3", "#24443A", "#C6EAD9"), frozenset({"calm", "serene", "peaceful", "comforted", "safe", "quiet", "clean", "white tea", "lavender", "linen", "spa", "mint"})),
    (VisualDirection("midnight", "#17162B", "#25223C", "#8D79D9", "#F5F1FF", "#3F336E"), frozenset({"grief", "sad", "melancholy", "heartbroken", "lonely", "mysterious", "dark", "night", "midnight", "incense", "smoke", "myrrh", "black", "noir"})),
    (VisualDirection("storm", "#E8EDF2", "#F8FAFC", "#6D8497", "#29333D", "#B9C9D6"), frozenset({"rain", "petrichor", "fog", "gray", "grey", "muted", "anxious", "overwhelmed", "restless", "ozone", "concrete", "cold"})),
    (VisualDirection("electric", "#15121F", "#271B3D", "#FF4FD8", "#F7F0FF", "#4FE8FF"), frozenset({"aldehydes", "electric", "neon", "metallic", "metallic accord", "chrome", "robotic", "futuristic", "cyberpunk", "city lights", "fluorescent", "synthetic", "intense", "bold"})),
    (VisualDirection("earth", "#F1E7D8", "#FBF6EE", "#8D6849", "#3D2E22", "#C9A97A"), frozenset({"earthy", "forest", "soil", "mossy", "vetiver", "oakmoss", "cedar", "woody", "green", "herbal", "garden", "grounded", "autumn"})),
    (VisualDirection("warmth", "#FFF0DE", "#FFF9F1", "#D98245", "#4B2D1D", "#FFC58D"), frozenset({"warm", "cozy", "vanilla", "cocoa", "amber", "gourmand", "cinnamon", "honey", "caramel", "comforting", "summer", "solar"})),
)
_DEFAULT_THEME = VisualDirection("neutral", "#F4F3F0", "#FFFFFF", "#8A8175", "#292724", "#DDD8CF")


def visual_direction(
    tags: Iterable[str], notes: Iterable[ScentRecommendation] = ()
) -> VisualDirection:
    """Resolve a palette from tag evidence and preserve top/heart/base anchors.

    Pass both values returned by ``recommend()`` so a GUI can use the note
    names as its top, heart, and base visual layers.
    """
    normalized = {tag.lower() for tag in tags}
    note_names: set[str] = set()
    note_layers: list[tuple[str, str]] = []
    for note in notes:
        normalized.update(tag.lower() for tag in note.matched_tags)
        note_names.add(note.name.lower())
        if not any(role == note.role for role, _ in note_layers):
            note_layers.append((note.role, note.name))

    best_theme, best_score = _DEFAULT_THEME, 0
    for theme, signals in _THEMES:
        score = len(normalized & signals)
        if score > best_score:
            best_theme, best_score = theme, score
    if best_score == 0:
        for theme, signals in _THEMES:
            score = len(note_names & signals)
            if score > best_score:
                best_theme, best_score = theme, score
    role_order = {"top": 0, "heart": 1, "base": 2}
    note_layers.sort(key=lambda item: role_order.get(item[0], len(role_order)))
    return replace(best_theme, note_layers=tuple(note_layers))
