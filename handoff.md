# You Left a Scent — Handoff Guide

## Overview

A deterministic scent recommendation engine that turns short "vibe" phrases (e.g. "robotic sunrise", "romantic night out") into 3–5 perfume notes using a local SQLite database. No AI — pure tag-based matching with fuzzy fallback.

## Repository Structure

```
you-left-a-scent/
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies (rapidfuzz, etc.)
├── you_left_a_scent/
│   ├── cli.py                       # CLI argument parsing and output
│   ├── data.py                      # Backward-compat catalog access
│   ├── matcher.py                   # Backward-compat matching imports
│   ├── database.py                  # Backward-compat DB queries
│   ├── catalog/                     # Seed data (the "knowledge base")
│   │   ├── notes.py                 # 110+ scent note definitions with tags
│   │   ├── categories.py            # Tag category groupings
│   │   ├── syntax.py                # Filler words filtered from input
│   │   └── aliases/                 # Vibe → tag mappings
│   │       ├── adjectives.py        # Texture/descriptor aliases
│   │       ├── aesthetics.py        # Aesthetic/style aliases (50+)
│   │       ├── colors.py            # Color → tag mappings
│   │       ├── emotions.py          # Emotion → tag mappings (45+)
│   │       ├── events.py            # Event/celebration aliases
│   │       ├── expressions.py       # Verb/expression aliases
│   │       ├── food_and_drinks.py   # Food/drink aliases (40+)
│   │       ├── places.py            # Location aliases (50+)
│   │       ├── scenarios.py         # Scenario aliases (40+)
│   │       └── seasons.py           # Season/weather aliases (40+)
│   ├── matching/                    # Matching engine
│   │   ├── matcher.py               # Core recommendation logic
│   │   ├── fuzzy.py                 # RapidFuzz fuzzy matching
│   │   ├── normalization.py         # Input text → normalized terms
│   │   ├── models.py                # ScentRecommendation dataclass
│   │   ├── repository.py            # SQLite query helpers
│   │   └── history.py               # Repeat-penalty history
│   └── db/                          # Database layer
│       ├── connection.py            # SQLite connection helpers
│       ├── schema.py                # Table creation + seed check
│       └── seed.py                  # Database seeding (SEED_VERSION = 21)
└── you_left_a_scent.db              # Auto-generated SQLite database
```

## How It Works

### Input → Output Pipeline

1. **Normalize** (`normalization.py`): Lowercase, filter filler words, then extract words plus 2- to 4-word phrases
2. **Match** (`matcher.py`):
   - Exact tag matches against `vibe_tags` table
   - Alias lookups against `vibe_aliases` table
   - Fuzzy fallback via `fuzzy.py` (RapidFuzz WRatio, cutoff 78)
3. **Score** (`matcher.py`): Notes scored by matched tags × weights, with repeat penalties
4. **Rank & Select**: Top 3–5 unique notes, ensuring concrete tag representation

### Key Design Decisions

- **No AI**: Fully deterministic, reproducible results
- **Local SQLite**: Portable, no external services
- **Repeat Penalties**: Same input gets variety across calls (history table)
- **Fallback Notes**: Notes with `is_fallback=1` used when no tags match
- **Fuzzy Matching**: Only for terms ≥ 4 chars; substring penalty applied to avoid false positives (e.g. "man" → "mandarin")

## How to Expand the Catalog

### Adding New Scent Notes

Edit `catalog/notes.py`. Each note needs:

```python
{'name': 'Note Name',
 'role': 'top' | 'heart' | 'base',
 'description': 'One-line evocative description.',
 'fallback': 0,  # 1 = shown when no tags match
 'tags': ['tag1', 'tag2', ...]},  # 5-7 specific tags
```

**Guidelines:**
- Keep tags specific, not generic (avoid overusing "clean", "soft", "warm")
- First tag is auto-derived from the note name (lowercased)
- Use existing tags when possible; add new tags sparingly
- Tags get auto-categorized via `categories.py`

### Adding New Aliases

Edit the appropriate file in `catalog/aliases/`. Each alias maps an input term → list of tags:

```python
"input phrase": ["tag1", "tag2", "tag3", ...],
```

**Guidelines:**
- Keep 5–7 tags per alias
- Tags should be scent-relevant (not abstract concepts)
- Multi-word phrases get a boost of 3; single-word get 2 (or 4 if exact match)
- For poetic language, add the conjugations people will actually type (for example, both `"fade"` and `"fading"`) and add a phrase when its combined meaning matters (for example, `"died tonight"`).

### Adding New Tag Categories

Edit `catalog/categories.py`. Add a new entry to `TAG_CATEGORIES`:

```python
("category_name", _group("tag1", "tag2", "tag3")),
```

This helps `category_for_tag()` classify tags for the matching engine.

### After Changes

1. Bump `SEED_VERSION` in `db/seed.py` (increment by 1)
2. Delete `you_left_a_scent.db` to force re-seed
3. Run `python main.py "your test vibe"` to verify

## Fuzzy Matching Details

Located in `matching/fuzzy.py`:

- **Scorer**: `rapidfuzz.fuzz.WRatio`
- **Cutoff**: 78 (base), 92 for substring matches
- **Min term length**: 4 characters (avoids "man" → "mandarin")
- **Word count guard**: Only matches terms with same word count
- **Substring penalty**: If input is a substring of candidate, requires score ≥ 92

## Testing

```bash
# Basic usage
python main.py "robotic sunrise"

# With custom count
python main.py -n 3 "romantic night out"

# Re-seed database
rm you_left_a_scent.db && python main.py "test"
```

## Common Pitfalls

- **Duplicate keys in alias dicts**: Python dicts silently keep last value. Check for duplicates when adding.
- **Over-tagging**: Too many generic tags (clean, soft, warm) make notes match everything → noisy results.
- **Fuzzy false positives**: Short terms (< 4 chars) are now skipped. Substring matches require higher score.
- **Seed version**: Always bump `SEED_VERSION` when changing catalog data, or the DB won't update.
