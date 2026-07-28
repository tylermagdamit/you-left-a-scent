# You Left a Scent

`You Left a Scent` is a small local fragrance-vibe generator. You give it a short phrase like `sad sunrise`, `job interview`, `desert`, or `liminal hallway`, and it returns 3 to 5 scent notes that fit the mood.

It does not use AI. The whole personality of the app comes from a curated SQLite-backed catalog of notes, tags, and aliases.

## Try It

Install the one external dependency:

```bash
pip install -r requirements.txt
```

Run a prompt:

```bash
python main.py "blue winter morning"
```

Or run it as a package:

```bash
python -m you_left_a_scent "grunge summer"
```

If you run it with no phrase, it will ask you for one:

```bash
python main.py
```

The first run creates `you_left_a_scent.db` in the project root. That database is generated locally from the Python catalog files.

## Example Prompts

Try phrases like:

- `sad sunrise`
- `early classroom morning`
- `job interview`
- `desert`
- `black velvet desert`
- `blue winter morning`
- `liminal hallway`
- `dreamcore classroom`
- `grunge summer`
- `dark academia library`
- `avant-garde gallery opening`

## How Matching Works

The app breaks your phrase into words and short phrases, then checks them against a local SQLite database.

It looks for:

- exact vibe tags, like `rain`, `rose`, `desert`, or `winter`
- curated aliases, like `job interview -> clean, polished, confident`
- fuzzy matches through RapidFuzz, like `sunrize ~= sunrise`

RapidFuzz is not AI. It only compares strings against the local catalog so the app can tolerate typos and near matches.

The app also keeps a tiny local recommendation history. If you run the same vibe again, it will try to move toward different notes instead of giving you the exact same blend every time.

## Project Structure

```text
you_left_a_scent/
  catalog/
    aliases/
      aesthetics.py
      colors.py
      emotions.py
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
    matcher.py
    models.py
    normalization.py
    repository.py
  cli.py
```

The older files `data.py`, `database.py`, and `matcher.py` are still there as thin compatibility wrappers. They keep old imports working while the real code lives in the organized subpackages.

The `catalog/syntax.py` file is the little language layer that strips out filler words like `the`, `by`, and `and` so the matcher can focus on the real content of a sentence.

## Adding More Vibes

Most creative expansion happens in two places.

Add new scent materials in:

```text
you_left_a_scent/catalog/notes.py
```

Add new prompt language in:

```text
you_left_a_scent/catalog/aliases/
```

Use `you_left_a_scent/catalog/aliases/food_and_drinks.py` for general meal, drink, and snack language.

For example, aesthetics belong in:

```text
you_left_a_scent/catalog/aliases/aesthetics.py
```

If you add new tags and want them grouped cleanly, update:

```text
you_left_a_scent/catalog/categories.py
```

When the seed data changes, bump `SEED_VERSION` in:

```text
you_left_a_scent/db/seed.py
```

That tells the app to refresh the generated SQLite database the next time it runs.

## Why This Design

The project is meant to stay lightweight and personal. SQLite gives it a real local database without needing a server. RapidFuzz gives it a little flexibility without turning it into an AI app. The catalog files keep the taste and logic visible, editable, and yours.
