"""Tag category definitions for the scent catalog."""

from __future__ import annotations

from collections import OrderedDict


def _group(*tags: str) -> set[str]:
    return set(tags)


TAG_CATEGORIES = OrderedDict(
    [
        ("futuristic", _group(
            "robotic", "futuristic", "metal", "metallic", "industrial", "silver", "city lights", "glossy",
            "synthetic", "plastic", "fluorescent", "chrome",
        )),
        ("fresh", _group("clean", "fresh", "fresh air", "bright", "crisp", "uplifting", "sunlit", "airy", "sparkling", "daylight", "sunrise", "dew")),
        ("romantic", _group("romantic", "date night", "night out", "velvet", "luminous", "flirty", "date", "soft focus", "intimate")),
        ("spicy", _group("spicy", "warm spice", "peppery", "cardamom", "ginger", "saffron", "bold", "smoldering", "cinnamon", "clove")),
        ("green", _group("green", "herbal", "botanical", "tea", "tea leaf", "matcha", "basil", "sage", "mint", "tomato leaf", "bamboo", "cypress")),
        ("floral", _group("floral", "rose", "jasmine", "orange blossom", "peony", "lavender", "neroli", "cherry blossom", "iris", "violet", "gardenia", "wisteria", "magnolia", "mimosa", "ylang ylang", "tuberose", "wildflower")),
        ("woody", _group("woody", "cedar", "cedarwood", "sandalwood", "cashmere wood", "architectural", "dry wood", "wood", "hinoki", "cypress", "pine")),
        ("smoky", _group("smoky", "smoke", "incense", "leather", "patchouli", "dark", "night", "ritual", "tobacco", "frankincense", "myrrh")),
        ("gourmand", _group("sweet", "vanilla", "tonka bean", "cocoa", "comforting", "cozy", "dessert", "soft sweet", "caramel", "salted caramel", "cotton candy", "buttery", "maple", "nutty", "baking")),
        ("marine", _group("marine", "sea salt", "ocean", "beach", "open air", "water", "ozone", "aquatic", "sea spray")),
        ("earthy", _group("earthy", "vetiver", "oakmoss", "forest", "grounded", "mossy", "rooted", "natural", "soil", "damp", "wet soil")),
        ("location", _group(
            "desert", "arid", "sand", "sunbaked", "cactus", "dry heat", "dunes", "chaparral",
            "classroom", "school", "office", "library", "garden", "mountain", "forest", "beach",
            "church", "hospital", "laundromat", "gas station", "parking lot", "mall", "arcade",
            "subway", "hotel lobby", "greenhouse", "attic", "basement", "hallway",
            "river", "lake", "waterfall", "meadow", "orchard", "vineyard", "coast", "harbor",
            "courtyard", "terrace", "lobby", "studio", "workshop", "clinic", "observatory",
        )),
        ("season", _group(
            "spring", "summer", "autumn", "fall", "winter", "snow", "frost", "cold", "harvest",
            "rainy season", "humid", "dry season", "stormy", "foggy", "heatwave", "monsoon",
        )),
        ("color", _group(
            "red", "pink", "orange", "yellow", "gold", "golden", "green", "blue", "navy",
            "purple", "violet", "black", "white", "silver", "grey", "gray", "brown",
            "cream", "clear", "neon", "pastel", "peach", "coral", "mint", "olive", "charcoal",
            "beige", "teal", "burgundy", "ivory", "blush", "tan", "sky blue", "cobalt",
        )),
        ("food_drink", _group(
            "mojito", "margarita", "espresso martini", "champagne", "wine", "whiskey", "rum", "tea", "coffee",
            "dessert", "picnic", "brunch", "coffee shop", "bakery", "street food", "lunch", "dinner",
            "late night snack", "smoothie", "sake", "chai", "maple syrup", "ginger ale", "coconut water",
            "honey tea", "mulled wine", "cherry soda", "fruit punch",
        )),
        ("event", _group(
            "birthday", "birthday party", "wedding", "anniversary", "graduation", "baby shower",
            "holiday party", "new year", "party", "celebration", "funeral", "reunion", "farewell",
            "date night", "concert", "carnival", "festival",
        )),
        ("aesthetic", _group(
            "grunge", "dreamcore", "weirdcore", "avant-garde", "liminal", "cottagecore",
            "dark academia", "light academia", "goth", "cyberpunk", "vaporwave", "fairycore",
            "coquette", "clean girl", "old money", "brutalist", "maximalist", "minimalist",
            "bohemian", "noir", "ethereal", "editorial", "abstract", "surreal", "empty",
            "soft girl", "dark feminine", "old hollywood", "coastal grandmother", "office siren",
            "techwear", "indie sleaze", "goblincore", "regencycore", "y2k", "fairygrunge",
            "monochrome", "dopamine dressing", "art hoe", "glassmorphism", "new romantic",
            "quiet luxury", "surrealist", "brutalist minimal", "neon noir",
            "zen", "wabi sabi", "solarpunk", "romantic realism",
        )),
        ("expression", _group(
            "love", "i love you", "adore", "miss you", "miss", "crave", "want", "need",
            "yearn", "cherish", "obsessed", "hate", "dream", "remember", "forget",
            "kiss", "kiss me", "linger", "escape", "protect", "heal", "shy", "hug", "touch",
            "blush", "whisper", "dance", "wander", "breathe", "hold", "embrace", "smile",
            "laugh", "cry", "run", "sleep", "hide", "forgive", "desire",
        )),
        ("texture", _group("dusty", "bitter", "sharp", "messy", "damp", "powdery", "creamy", "dry", "dirty", "grimy", "wet", "sticky", "fuzzy", "smooth", "salty", "sweet", "cold", "warm", "clean", "juicy", "tart", "waxy")),
        ("modern_materials", _group(
            "ambroxan", "iso e super", "cashmeran", "hedione", "galaxolide", "calone",
            "orris butter", "ambrette", "champagne accord",
        )),
        ("clean", _group("spa", "white shirt", "minimal", "muted", "skin", "soft", "quiet", "polished", "linen", "eucalyptus", "cotton", "white musk")),
        ("citrus", _group("citrus", "bergamot", "grapefruit", "lemon", "neroli", "orange", "mandarin", "yuzu", "lime")),
        ("emotion", _group(
            "sad", "melancholy", "lonely", "grief", "heartbroken", "nostalgic", "bittersweet",
            "hopeful", "joyful", "happy", "euphoric", "peaceful", "calm", "anxious", "restless",
            "angry", "confident", "sensual", "dreamy", "mysterious", "comforted", "vulnerable",
            "jealous", "homesick", "embarrassed", "curious", "focused", "burned out",
            "overwhelmed", "in love", "homesafe", "serene", "wistful", "longing", "content",
            "tender", "playful", "detached", "safe", "ashamed", "desperate", "grateful", "intense",
            "excited", "cozy", "reflective", "melancholic", "energetic",
        )),
        ("luxury", _group("luxury", "amber", "labdanum", "benzoin", "saffron", "golden", "elegant", "smooth", "expensive", "white amber", "rich")),
        ("fruit", _group("fruit", "citrus", "apple", "pear", "plum", "berry", "lychee", "rhubarb", "grape", "cherry", "tropical", "juicy")),
        ("time_of_day", _group("morning", "sunrise", "daylight", "afternoon", "evening", "dusk", "twilight", "night", "midnight", "golden hour")),
        ("weather", _group("rain", "snow", "frost", "fog", "foggy", "stormy", "windy", "overcast", "humid", "dry", "mist", "dew")),
        ("cultural", _group("japanese", "mediterranean", "tropical", "oriental", "zen", "minimal", "bohemian")),
    ]
)


def category_for_tag(tag: str) -> str:
    normalized = tag.lower()
    for category, tags in TAG_CATEGORIES.items():
        if normalized in tags:
            return category
    return "general"
