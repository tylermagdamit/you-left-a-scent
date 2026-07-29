# You Left a Scent

`You Left a Scent` is a small local fragrance-vibe generator.
You type in a short sentence like `kiss`, `moonlight`, `brutalist concrete`, or `job interview`, and it returns scent notes that fit the mood.

It does not use AI.
Everything comes from a PostgreSQL database seeded from curated Python catalogs.

## What It Does

- Takes short vibe phrases or sentence-like inputs
- Strips filler words like `the`, `by`, and `and`
- Matches exact tags, curated aliases, and fuzzy spellings
- Uses aliases as input-to-tag translations; notes rank from the resulting tags
- Returns 5 notes by default, with `-n` settable from 3 to 5
- Avoids repeating the exact same notes for repeated prompts by using local history
- Produces a broad visual direction and color palette a future GUI can use
- Uses lowercase, soft-spoken note descriptions while preserving each material's character

## Run It

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run a vibe:

```powershell
python main.py "moonlight"
```

Or with the Python launcher you already have:

```powershell
& 'C:\Users\tyler\AppData\Local\Python\pythoncore-3.14-64\python.exe' main.py "brutalist concrete"
```

If you leave off the phrase, the app will ask you for one.

## Good Inputs To Try

- `kiss`
- `moonlight`
- `dirty`
- `sad sunrise`
- `early classroom morning`
- `job interview`
- `desert`
- `blue winter morning`
- `liminal hallway`
- `dreamcore classroom`
- `grunge summer`
- `brutalist concrete`
- `dark academia library`
- `avant-garde gallery opening`
- `you died tonight`
- `i am falling apart beneath the moon`

## How It Works

The app is fully local and rule-based.
It uses:

- a note catalog in `you_left_a_scent/catalog/notes.py`
- alias groups in `you_left_a_scent/catalog/aliases/`
- tag categories in `you_left_a_scent/catalog/categories.py`
- PostgreSQL schema and seeding in `you_left_a_scent/db/`
- deterministic matching logic in `you_left_a_scent/matching/`

RapidFuzz is used only for string matching against the local catalog.
It is not AI.
It just helps the app catch typos and near-matches without needing a model.

## Project Layout

```text
you_left_a_scent/
  catalog/
    aliases/
      adjectives.py
      aesthetics.py
      colors.py
      emotions.py
      events.py
      expressions.py
      food_and_drinks.py
      places.py
      scenarios.py
      seasons.py
    syntax.py
    categories.py
    notes.py
  db/
    connection.py
    schema.py
    seed.py
  matching/
    fuzzy.py
    history.py
    matcher.py
    models.py
    normalization.py
    repository.py
    visuals.py
  cli.py
```

The legacy wrapper files `data.py`, `database.py`, and `matcher.py` are still present for compatibility.
The real code now lives in the structured subpackages above.

## Editing The Catalog

If you want to add new scent materials, edit:

```text
you_left_a_scent/catalog/notes.py
```

Each entry has a lower-case, concrete scent description and focused tags. Use
tags for smell facets people might type, such as `citrus peel`, `wet stone`,
`petals`, `dry wood`, or `paper fiber`; avoid broad catch-all tags.

If you want to teach the app new language like emotions, verbs, poetic phrases, adjectives, seasons, places, or aesthetics, edit:

```text
you_left_a_scent/catalog/aliases/
```

If you add new tag types and want them categorized cleanly, update:

```text
you_left_a_scent/catalog/categories.py
```

If the seed data changes, bump:

```text
you_left_a_scent/db/seed.py
```

That tells the app to refresh the PostgreSQL catalog the next time it starts.

An alias is an input-to-tag translation. For example, `"night market"` maps to
tags including `spicy`, `ginger`, `smoke`, and `neon`; notes carrying those tags
are then ranked. A tag already attached directly to a note, such as
`paper fiber`, also works as an input without a separate alias.

## A Good Mental Model

Think of this project like a tiny curated scent dictionary.
The catalog defines the taste, the aliases teach the app how people actually speak, and PostgreSQL holds the finished database.

## PostgreSQL Setup

The app reads its connection string from `DATABASE_URL`:

```powershell
$env:DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:8888/you_left_a_scent"
python main.py "paper fiber"
```

On the first run, the app creates its tables and seeds the notes, tags, aliases,
and visual data automatically. Do not commit a database password or connection
string. For a deployed app, set `DATABASE_URL` in the hosting provider's
environment-variable settings.

That keeps the app lightweight, editable, and very much yours.

## Visual Directions for a GUI

`visual_direction(matched_tags, notes)` groups detailed scent evidence into
eight broad families: `sunlit`, `blush`, `stillness`, `midnight`, `storm`,
`electric`, `earth`, and `warmth`. It returns five hex colors plus the first
returned `top`, `heart`, and `base` note names as `note_layers`, so the GUI can
use the scent's existing fields as visual anchors. Matched tags choose the
family; note names are only a fallback. Happy/bright/citrus inputs,
for example, resolve to the yellow-accented `sunlit` theme.

```python
from you_left_a_scent.matching import recommend, visual_direction

notes, matched_tags = recommend(conn, vibe_text)
theme = visual_direction(matched_tags, notes)
```

`theme` provides `background`, `surface`, `accent`, `text`, `glow`, and
`note_layers` (the selected top/heart/base notes) for a GUI.
