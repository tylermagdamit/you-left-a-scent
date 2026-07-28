"""Tag category definitions for the scent catalog."""

from __future__ import annotations

from collections import OrderedDict


def _group(*tags: str) -> set[str]:
    return set(tags)


TAG_CATEGORIES = OrderedDict(
    [
        ("futuristic", _group(
            "robotic", "futuristic", "metal", "metallic", "industrial", "silver", "city lights", "glossy",
            "synthetic", "plastic", "fluorescent",
        )),
        ("fresh", _group("clean", "fresh", "fresh air", "bright", "crisp", "uplifting", "sunlit", "airy", "sparkling", "daylight", "sunrise")),
        ("romantic", _group("romantic", "date night", "night out", "velvet", "luminous", "flirty", "date", "soft focus")),
        ("spicy", _group("spicy", "warm spice", "peppery", "cardamom", "ginger", "saffron", "bold", "smoldering")),
        ("green", _group("green", "herbal", "botanical", "tea", "tea leaf", "matcha", "basil", "sage", "mint")),
        ("floral", _group("floral", "rose", "jasmine", "orange blossom", "peony", "lavender", "neroli", "cherry blossom", "iris", "violet")),
        ("woody", _group("woody", "cedar", "cedarwood", "sandalwood", "cashmere wood", "architectural", "dry wood")),
        ("smoky", _group("smoky", "smoke", "incense", "leather", "patchouli", "dark", "night", "ritual")),
        ("gourmand", _group("sweet", "vanilla", "tonka bean", "cocoa", "comforting", "cozy", "dessert", "soft sweet")),
        ("marine", _group("marine", "sea salt", "ocean", "beach", "open air", "water", "ozone")),
        ("earthy", _group("earthy", "vetiver", "oakmoss", "forest", "grounded", "mossy", "rooted", "natural", "soil", "damp")),
        ("location", _group(
            "desert", "arid", "sand", "sunbaked", "cactus", "dry heat", "dunes", "chaparral",
            "classroom", "school", "office", "library", "garden", "mountain", "forest", "beach",
            "church", "hospital", "laundromat", "gas station", "parking lot", "mall", "arcade",
            "subway", "hotel lobby", "greenhouse", "attic", "basement", "hallway",
        )),
        ("season", _group(
            "spring", "summer", "autumn", "fall", "winter", "snow", "frost", "cold", "harvest",
            "rainy season", "humid", "dry season", "stormy", "foggy", "heatwave", "monsoon",
        )),
        ("color", _group(
            "red", "pink", "orange", "yellow", "gold", "golden", "green", "blue", "navy",
            "purple", "violet", "black", "white", "silver", "grey", "gray", "brown",
            "cream", "clear", "neon", "pastel",
        )),
        ("food_drink", _group(
            "mojito", "margarita", "espresso martini", "champagne", "wine", "whiskey", "rum", "tea", "coffee",
            "dessert", "picnic", "brunch", "coffee shop", "bakery", "street food", "lunch", "dinner",
            "late night snack",
        )),
        ("event", _group(
            "birthday", "birthday party", "wedding", "anniversary", "graduation", "baby shower",
            "holiday party", "new year", "party", "celebration", "funeral", "reunion", "farewell",
            "date night", "concert",
        )),
        ("aesthetic", _group(
            "grunge", "dreamcore", "weirdcore", "avant-garde", "liminal", "cottagecore",
            "dark academia", "light academia", "goth", "cyberpunk", "vaporwave", "fairycore",
            "coquette", "clean girl", "old money", "brutalist", "maximalist", "minimalist",
            "bohemian", "noir", "ethereal", "editorial", "abstract", "surreal", "empty",
        )),
        ("expression", _group(
            "love", "i love you", "adore", "miss you", "miss", "crave", "want", "need",
            "yearn", "cherish", "obsessed", "hate", "dream", "remember", "forget",
        )),
        ("texture", _group("dusty", "bitter", "sharp", "messy", "damp", "powdery", "creamy", "dry")),
        ("luxury", _group("luxury", "amber", "labdanum", "benzoin", "saffron", "golden", "elegant", "smooth", "expensive")),
        ("clean", _group("spa", "white shirt", "minimal", "muted", "skin", "soft", "quiet", "polished")),
        ("citrus", _group("citrus", "bergamot", "grapefruit", "lemon", "neroli", "orange")),
        ("emotion", _group(
            "sad", "melancholy", "lonely", "grief", "heartbroken", "nostalgic", "bittersweet",
            "hopeful", "joyful", "happy", "euphoric", "peaceful", "calm", "anxious", "restless",
            "angry", "confident", "sensual", "dreamy", "mysterious", "comforted", "vulnerable",
            "jealous", "homesick", "embarrassed", "curious", "focused", "burned out",
            "overwhelmed", "in love", "homesafe",
        )),
    ]
)


def category_for_tag(tag: str) -> str:
    normalized = tag.lower()
    for category, tags in TAG_CATEGORIES.items():
        if normalized in tags:
            return category
    return "general"
