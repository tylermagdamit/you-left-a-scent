# You Left a Scent

`You Left a Scent` is a small local fragrance-vibe generator.
You type in a short sentence like `kiss`, `moonlight`, `brutalist concrete`, or `job interview`, and it returns scent notes that fit the mood.

It does not use AI.
Everything comes from a local SQLite database that is generated from curated Python catalogs.

## What It Does

- Takes short vibe phrases or sentence-like inputs
- Strips filler words like `the`, `by`, and `and`
- Matches exact tags, curated aliases, and fuzzy spellings
- Returns 5 notes by default, with `-n` settable from 3 to 5
- Avoids repeating the exact same notes for repeated prompts by using local history

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

## How It Works

The app is fully local and rule-based.
It uses:

- a note catalog in `you_left_a_scent/catalog/notes.py`
- alias groups in `you_left_a_scent/catalog/aliases/`
- tag categories in `you_left_a_scent/catalog/categories.py`
- SQLite schema and seeding in `you_left_a_scent/db/`
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
  cli.py
```

The legacy wrapper files `data.py`, `database.py`, and `matcher.py` are still present for compatibility.
The real code now lives in the structured subpackages above.

## Editing The Catalog

If you want to add new scent materials, edit:

```text
you_left_a_scent/catalog/notes.py
```

If you want to teach the app new language like emotions, verbs, adjectives, seasons, places, or aesthetics, edit:

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

That tells the app to refresh the generated SQLite database the next time it starts.

## A Good Mental Model

Think of this project like a tiny curated scent dictionary.
The catalog defines the taste, the aliases teach the app how people actually speak, and SQLite holds the finished local database.

That keeps the app lightweight, editable, and very much yours.
