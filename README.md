# You Left a Scent

A local, SQLite-backed fragrance vibe generator.

## What it does

You type a short phrase like:

- `robotic sunrise`
- `romantic night out`
- `quiet rainy commute`

The app looks up vibe tags in a local SQLite database and returns 3 to 5 scent notes that match the mood.

## How it is built

- `you_left_a_scent/data.py` holds the seed library for notes and vibe tags.
- `you_left_a_scent/database.py` creates and seeds the SQLite database.
- `you_left_a_scent/matcher.py` scores the vibe locally with deterministic keyword matching.
- `you_left_a_scent/cli.py` handles the terminal interface.

## Run it

Install dependencies first:

```bash
pip install -r requirements.txt
```

```bash
python main.py "romantic night out"
```

Or:

```bash
python -m you_left_a_scent "robotic sunrise"
```

The first run creates `you_left_a_scent.db` in the project root.

Matching is still local and database-driven. RapidFuzz only helps compare user input against the local tags and aliases.
