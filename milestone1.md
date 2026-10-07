# Milestone 1: Read the data and run the starter

Completed October 7, 2026 using the repository's `.venv` Python interpreter.

## Listing fields

Each listing contains `id` (string), `title` (string), `description` (string),
`category` (string), `style_tags` (list of strings), `size` (string),
`condition` (string), `price` (float), `colors` (list of strings),
`brand` (string or null), and `platform` (string).

Three fields to remember: `size`, `price`, and `style_tags`.
Size and price constrain search results; titles, descriptions, and style tags
provide text for matching the requested item.

## Six listings read in full

Ran `python app.py listings --full -n 6` and read every field in each record:

| ID | Item | Size | Price | Platform | Brand |
|---|---|---|---|---|---|
| lst_001 | Vintage Levi's 501 Jeans — Medium Wash | W30 L30 | $38 | depop | Levi's |
| lst_002 | Y2K Baby Tee — Butterfly Print | S/M | $18 | depop | null |
| lst_003 | Oversized Flannel Shirt — Plaid Red/Black | XL (oversized) | $22 | thredUp | Woolrich |
| lst_004 | 90s Track Jacket — Navy/White Stripe | M | $45 | poshmark | Champion |
| lst_005 | Corduroy Wide-Leg Pants — Rust | W28 | $32 | depop | null |
| lst_006 | Graphic Tee — 2003 Tour Bootleg Style | L | $24 | depop | null |

The descriptions include fit and condition details, such as the baby tee's
medium tag but small fit, and pilling on the corduroy pants. Search must account
for composite sizes such as `S/M`; a plain substring match would incorrectly
match `L` with `XL` or `S` with `US 9`. Brand cannot be assumed present.
The data consists of 40 local mock listings, rather than live marketplace results.

## Wardrobe shape

Ran `python app.py fields` and read `data/wardrobe_schema.json`.
The wardrobe passed to `suggest_outfit` is a dictionary with an `items` list.
Each item contains `id`, `name`, `category`, `colors`, `style_tags`, and `notes`.
Notes may be null. The example wardrobe has 10 items, including jeans,
tops, a denim jacket, sneakers, boots, a belt, and a bag.

An empty wardrobe returned by `get_empty_wardrobe()` is exactly:

```json
{"items": []}
```

The loader removes underscore-prefixed documentation keys from the JSON
templates. An empty wardrobe therefore has the same shape as a populated one.

## Starter run

Ran `python app.py examples`, then the requested query with single quotes:

```text
$ python app.py ask 'vintage graphic tee under $30'

  The planning loop isn't built yet — see the TODO in agent.py.

0 model calls this session
```

This is the expected starter behavior: the CLI runs, but the agent and tools
are still stubs. No acceptance-criterion evaluation was performed.

## Environment check

Ran `python test.py` in the virtual environment:

```text
10 passed, 0 failed, 0 to look at, 0 skipped
```

Python 3.11.9, dependencies, MCP imports, data loading, and the real model call
all passed. The environment check made one model request; the starter query
made none.
