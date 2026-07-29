# You Left a Scent — Handoff Guide

## Overview

`You Left a Scent` is a deterministic, local fragrance-vibe engine. It turns a
phrase or short sentence into three to five scent notes, matched tags, and a
GUI-ready visual direction. It uses a curated Python catalog and SQLite; it
does not use AI or external services.

## Current Architecture

```text
main.py                         # Entry point
you_left_a_scent/
  cli.py                        # CLI output, including visual direction
  catalog/
    notes.py                    # 130 note records: name, role, description, tags
    categories.py               # Fine-grained tag categories
    syntax.py                   # Filler words for sentence parsing
    aliases/                    # Input phrase -> tag mappings
  db/
    seed.py                     # SQLite seed version and catalog seeding
    schema.py
    connection.py
  matching/
    normalization.py            # Words + 2- to 4-word phrase extraction
    matcher.py                  # Exact, alias, fuzzy matching, ranking
    fuzzy.py                    # RapidFuzz fallback safeguards
    history.py                  # Repeat penalties
    models.py                   # ScentRecommendation
    repository.py               # SQLite lookups
    visuals.py                  # GUI palette and note-layer resolver
```

## Input to Output

1. `normalization.py` lowercases input, removes filler words, and preserves
   individual words plus two- to four-word phrases.
2. `matcher.py` finds exact direct-tag matches and curated alias matches, then
   uses guarded fuzzy matching for spelling and close phrasing.
3. Matched tags score notes with the same tags. The engine balances note roles,
   avoids recently repeated results, and returns 3–5 notes.
4. `visual_direction(matched_tags, notes)` resolves a GUI palette and returns
   selected top/heart/base notes as visual layers.

Aliases are input-to-tag translations. For example:

```python
"night market": ["spicy", "ginger", "smoke", "neon", "citrus", "warm", "electric"]
```

The notes carrying those tags are ranked. Direct tags on a note, such as
`paper fiber`, also match input without a separate alias.

## Catalog Editing

### Notes

Edit `you_left_a_scent/catalog/notes.py`.

```python
{
    "name": "Example Note",
    "role": "top",  # top, heart, or base
    "description": "lower-case, concrete scent description",
    "fallback": 0,
    "tags": ["specific material", "scent facet", "texture"],
}
```

Descriptions should say how the material smells: ingredients, texture, and
odor facets first. Keep them lower-case and concise; avoid abstract emotional
or generic atmospheric claims.

Tags should be specific and useful as user input. Good examples include
`citrus peel`, `wet stone`, `petals`, `dry wood`, `paper fiber`, `amber resin`,
and `balsamic`. Avoid assigning broad tags such as `clean`, `soft`, or `warm`
to every note because they make recommendations noisy.

### Aliases

Edit the relevant module in `catalog/aliases/` for places, scenarios, events,
food and drink, seasons/weather, colors, aesthetics, emotions, expressions,
or descriptors.

```python
"input phrase": ["tag1", "tag2", "tag3"],
```

Use existing note tags whenever possible. Add the verb forms people will type
when appropriate, and add a multi-word alias when the combined phrase has a
distinct meaning.

### Categories

`catalog/categories.py` classifies tags for matching. Add a category only when
it improves organization; it is not required for every new tag.

## Visual Directions for a GUI

`matching/visuals.py` maps matched tags into one of eight broad visual families:

- `sunlit`
- `blush`
- `stillness`
- `midnight`
- `storm`
- `electric`
- `earth`
- `warmth`

Use it after recommendations:

```python
from you_left_a_scent.matching import recommend, visual_direction

notes, matched_tags = recommend(conn, vibe_text)
theme = visual_direction(matched_tags, notes)
```

`theme` contains `background`, `surface`, `accent`, `text`, and `glow` hex
colors, plus `note_layers`: the first returned top, heart, and base note names.
Matched tags choose the family; note names are used only as a fallback. Update
the signal tags or hex values in `visuals.py` to tune the visual system; no DB
reseed is required for that change.

## Database Refresh and Verification

When changing `notes.py`, aliases, or categories:

1. Increment `SEED_VERSION` in `you_left_a_scent/db/seed.py`.
2. Run a test prompt. Initialization detects the new version and refreshes the
   local SQLite database automatically.

```powershell
python main.py "night market"
python main.py "paper fiber"
python main.py "dark academia library"
```

## Matching Safeguards

- RapidFuzz uses `WRatio` with a base cutoff of 78.
- Terms shorter than four characters skip fuzzy matching.
- Candidate and input must have the same word count.
- Substring matches require a score of at least 92.
- When a phrase is recognized exactly, its component words are excluded from
  fuzzy matching to avoid unrelated results such as `apart` matching `party`.

## Common Pitfalls

- Duplicate keys in an alias dictionary silently overwrite earlier entries.
- Alias tags that no note carries will not help recommendation ranking.
- Broad tags on too many notes make results less distinctive.
- Catalog changes require a `SEED_VERSION` bump before they appear in SQLite.
