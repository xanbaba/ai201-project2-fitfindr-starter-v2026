# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> The three tools and planning loop are implemented. `ask` searches the local
> listings, suggests an outfit, and writes a caption, or stops when search is empty.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr is a command-line thrift assistant that takes a request such as
`vintage graphic tee under $30, size M` and searches 40 local mock listings.
It filters by size and budget, ranks keyword matches, and selects the first
result. Using the example wardrobe supplied by the CLI, it suggests an outfit
and writes a short caption with the item's title, price, and platform; an empty
wardrobe gets general styling advice. If no listing matches, it stops before
the outfit and caption tools and tells the user what search constraints to change.

Repository for Units 3 and 4:
[xanbaba/ai201-project2-fitfindr-starter-v2026](https://github.com/xanbaba/ai201-project2-fitfindr-starter-v2026).
Keep this same repository and its commit history for the next unit.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the local mock listings by keyword overlap, with optional size and inclusive price filters, and ranks the matching items.
- **Inputs:** `description` (`str`), containing item keywords; `size` (`str | None`, default `None`), containing a size label; `max_price` (`float | None`, default `None`), the maximum listing price in US dollars. `None` skips the corresponding filter. Match sizes case-insensitively as complete labels: `M` matches `M`, `S/M`, and `M/L`; `L` matches `L` and `L/XL`, but not `XL`; ignore parenthesized fit notes. Numeric shoe sizes such as `8` match `US 8`, but not `US 8.5`; waist labels such as `W30` match the waist in `W30 L30`. One-size listings match only an explicit `One Size` request, not an arbitrary clothing size.
- **Returns:** A `list[dict]` of at most `config.SEARCH_RESULT_LIMIT` original listing records, each containing `id` (`str`), `title` (`str`), `description` (`str`), `category` (`str`), `style_tags` (`list[str]`), `size` (`str`), `condition` (`str`), `price` (`float`), `colors` (`list[str]`), `brand` (`str | None`), and `platform` (`str`). Tokenize the description and each listing's title, description, and style tags into lowercase alphanumeric words; score each eligible listing by the count of distinct query words present in those fields. Keep positive scores, sort by descending score, then ascending price, then ascending ID. Every returned item must satisfy the supplied size and price filters; prices equal to `max_price` are allowed.
- **When it has nothing:** Returns `[]` when no listing passes the filters with a positive keyword score, or when the description has no alphanumeric words. Never returns `None` for no matches.

### `suggest_outfit`

- **What it does:** Uses the model through `generate()` to suggest one or two outfits combining the selected listing with the user's wardrobe.
- **Inputs:** `new_item` (`dict`), one complete listing record in the shape returned by `search_listings`; `wardrobe` (`dict`), with an `items` key containing a `list[dict]` of owned pieces. Each wardrobe piece has `id` (`str`), `name` (`str`), `category` (`str`), `colors` (`list[str]`), `style_tags` (`list[str]`), and optional `notes` (`str | None`). A missing brand or null notes must not be presented as the text `None`.
- **Returns:** A non-empty `str` describing one or two outfits that include the selected item and name the owned pieces used, with a short explanation of how the colors or style work together. The prompt must distinguish owned pieces from any additional styling suggestions so it does not claim the user owns an unlisted item.
- **When it has nothing:** For `wardrobe={"items": []}`, returns non-empty general styling advice for the selected item, clearly stating that no wardrobe items are saved. If the model returns only whitespace, returns `No outfit suggestions were generated. Try again.`; if the service cannot be reached, propagates `ModelUnavailable` from the supplied adapter.

### `create_fit_card`

- **What it does:** Uses the model through `generate()` to turn the outfit suggestion and selected listing into a short caption someone could post.
- **Inputs:** `outfit` (`str`), the styling text returned by `suggest_outfit`; `new_item` (`dict`), the same complete listing record used for the outfit suggestion, including its title, price, platform, colors, and style tags; `brand` may be null.
- **Returns:** A non-empty `str` containing a two-to-four sentence caption that mentions the item, its listing price in US dollars, and its platform once each, and describes a specific outfit or style from `outfit`. The prompt asks for a casual post without invented brand names or listing details; these are intended model-output requirements, to be measured later rather than assumed guaranteed.
- **When it has nothing:** For empty or whitespace-only `outfit`, returns `No outfit was provided, so a fit card could not be created.` without calling the model. If the model returns only whitespace, returns `No fit card was generated. Try again.`; if the service cannot be reached, propagates `ModelUnavailable` from the supplied adapter.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, set `session["error"]` to `No matching listings found. Try different keywords, a different size, or a higher budget.` and return the session immediately, without calling `suggest_outfit` or `create_fit_card`. Otherwise, store the first result in `session["selected_item"]`, call `suggest_outfit` with that stored item and the session wardrobe, then call `create_fit_card` with the stored outfit suggestion and the same selected item.

**Where it lives:** `agent.py::run_agent`

The loop uses four stages: parse, search, outfit, and card. Every iteration calls
`trace.check_iterations()` before running its stage; `config.MAX_ITERATIONS`
limits the run. An empty search returns after the second stage, while a match
advances through all four.

**How the query is parsed:** Regular expressions in `agent.py::_parse_query` extract an explicit price ceiling after `under`, `below`, `up to`, `max`, `maximum`, or `budget`, and a size after `size` (optionally preceded by `in`). Supported size labels include clothing labels and composites, `One Size`, numeric or `US` shoe sizes, and waist/inseam labels such as `W30 L30`. The parser removes those clauses, strips a leading phrase such as `looking for` or `find me`, and uses the remaining text as the description. Omitted filters become `None`; this is a limited parser for these formats, not general natural-language understanding. `under $30` sets an inclusive ceiling of 30.0, as defined in the search contract.

**What moves through the session:** `query` and `wardrobe` initialize the session. Parsing writes `parsed`; search reads `parsed` and writes `search_results`; the first result becomes `selected_item`. Outfit generation reads `selected_item` and `wardrobe` and writes `outfit_suggestion`. Caption generation reads `outfit_suggestion` and the same `selected_item` and writes `fit_card`. An empty search instead sets `error`, leaving `selected_item`, `outfit_suggestion`, and `fit_card` as `None`. Every downstream argument is read back from the session.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30, size M'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here is a practical, thrift-styled outfit utilizing the selected listing and your owned wardrobe pieces:

### Outfit: Y2K Streetwear Casual

**The Look:**
* **Top:** Y2K Baby Tee — Butterfly Print *(Selected Listing)*
* **Bottoms:** Baggy straight-leg jeans, dark wash *(Owned piece: w_001)*
* **Outerwear:** Vintage black denim jacket *(Owned piece: w_006)*
* **Shoes:** Chunky white sneakers *(Owned piece: w_007)*
* **Accessories:** Black crossbody bag *(Owned piece: w_005)*
* *Suggestion (Not owned):* Silver chain necklace to complement the Y2K aesthetic

**Why it works:**
This outfit plays with proportions by balancing the fitted, cropped nature of the butterfly baby tee with the voluminous silhouette of the high-waisted, baggy dark wash jeans. The white in the baby tee ties directly into the chunky white sneakers, creating a cohesive color bridge from top to bottom. Layering the slightly cropped vintage black denim jacket over top keeps the streetwear edge sharp while offering a tonal black foundation that lets the pink and purple butterfly graphic stand out.

  Fit card: Score! I finally found this Y2K Baby Tee — Butterfly Print on Depop for just $18.00. I am styling it today with baggy dark-wash jeans, a black denim jacket, and chunky white sneakers for the ultimate early-2000s streetwear look.

0 model calls this session, 2 served from cache
```

**Empty search and state checks**

```text
$ python app.py ask 'designer ballgown size XXS under $5'

  No matching listings found. Try different keywords, a different size, or a higher budget.

0 model calls this session
```

Both full session dictionaries were also printed from `run_agent`. Wrappers
around the real outfit and caption tools captured deep copies of their actual
inputs without replacing their responses. In the matching run,
`search_results[0]`, `selected_item`, and both captured `new_item` arguments
were equal in every field, with ID `lst_002`; the captured caption input also
equaled `outfit_suggestion`. In the impossible run, neither downstream wrapper
was called, `search_results` was `[]`, and `selected_item`,
`outfit_suggestion`, and `fit_card` were all `None`.

These were individual integration checks with development caching enabled,
not the five-try acceptance evaluation. Additional checks verified parsed
filters, numeric half-size shoes, waist/inseam labels, optional filters, and
the iteration guard. Reading the empty-search message as a new user, the next
actions are concrete: try other item keywords, change the size, or raise the
budget. No rewrite of the specified message was needed.

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', size='M', max_price=30))"
[{'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[1], get_example_wardrobe()))"
Here is a practical, thrift-styled outfit utilizing the selected listing and your owned wardrobe pieces:

### Outfit: Y2K Streetwear Casual

**The Look:**
* **Top:** Y2K Baby Tee — Butterfly Print *(Selected Listing)*
* **Bottoms:** Baggy straight-leg jeans, dark wash *(Owned piece: w_001)*
* **Outerwear:** Vintage black denim jacket *(Owned piece: w_006)*
* **Shoes:** Chunky white sneakers *(Owned piece: w_007)*
* **Accessories:** Black crossbody bag *(Owned piece: w_005)*
* *Suggestion (Not owned):* Silver chain necklace to complement the Y2K aesthetic

**Why it works:**
This outfit plays with proportions by balancing the fitted, cropped nature of the butterfly baby tee with the voluminous silhouette of the high-waisted, baggy dark wash jeans. The white in the baby tee ties directly into the chunky white sneakers, creating a cohesive color bridge from top to bottom. Layering the slightly cropped vintage black denim jacket over top keeps the streetwear edge sharp while offering a tonal black foundation that lets the pink and purple butterfly graphic stand out.
```

```
$ python -c "import config; config.CACHE_ENABLED=False; from tools import create_fit_card; from utils.data_loader import load_listings; item=load_listings()[1]; [print('Caption '+str(i+1)+': '+create_fit_card('Pair the tee with baggy dark-wash jeans and chunky white sneakers for a relaxed Y2K streetwear outfit.', item)) for i in range(3)]"
Caption 1: Scored this adorable Y2K Baby Tee — Butterfly Print while browsing online. I am totally obsessed with the retro pastel graphics. I picked it up on depop for just $18.00 and cannot wait to wear it. Try styling it with baggy dark-wash jeans and chunky white sneakers for a relaxed Y2K streetwear outfit.
Caption 2: I am obsessed with this Y2K Baby Tee — Butterfly Print I just scored. I found it on depop for only $18.00 and the fit is unreal. I am planning to style it with baggy dark-wash jeans and chunky white sneakers for a relaxed Y2K streetwear outfit.
Caption 3: I am obsessed with this Y2K Baby Tee — Butterfly Print I just scored. I found it on depop for only $18.00 and it is in such great shape. I am planning to style it with baggy dark-wash jeans and chunky white sneakers for a relaxed Y2K streetwear outfit.
```

These commands were run with `.venv\Scripts\python.exe` on Windows. The caption
command disables caching only for that process; `TEMPERATURE` remains 0.9 and
normal development caching remains enabled. All three captions differ, although
the last two share an opening sentence. These are standalone tool checks, not
the five-try acceptance evaluation for Unit 4.

The search output follows the keyword-overlap contract: the mesh top mentions
"graphic tee" in its description and ties with the baby tee, so its lower price
puts it first. This shows a relevance limitation of the simple scoring rule.
The outfit output names the correct owned bag but gives its ID as `w_005`;
the actual bag ID is `w_010`. The model's item references need later scrutiny.

**Empty-case checks**

```text
$ python -c "from tools import suggest_outfit,create_fit_card; from utils.data_loader import get_empty_wardrobe,load_listings; print('Empty wardrobe: '+suggest_outfit(load_listings()[1],get_empty_wardrobe())); print('Empty outfit: '+create_fit_card('   ',load_listings()[1]))"
Empty wardrobe: No wardrobe items are saved. Here are two general styling ideas for this Y2K butterfly baby tee based on its fitted crop silhouette and nostalgic color palette:

**1. The Classic Y2K Streetwear Look**
* **The Vibe:** Early 2000s mall-goth meets pop princess.
* **How to style it:** Pair the baby tee with low-rise baggy cargo pants in olive green or classic denim to balance out the fitted crop of the shirt. Add a chunky platform sneaker or a retro shoulder bag to lean fully into the era's aesthetic.

**2. Soft Pastel Casual**
* **The Vibe:** Easy, everyday vintage-inspired streetwear.
* **How to style it:** Play up the pink and purple tones in the butterfly graphic by pairing the tee with a pleated white tennis skirt or light-wash straight-leg jeans. Layer with a thin zip-up hoodie left open and finish the outfit with retro canvas sneakers.

**Color Palette Note:** The white, pink, and purple combination makes this piece very easy to anchor with neutral bottoms (like denim, white, or black) while using accessories in matching pinks or purples to tie the look together.
Empty outfit: No outfit was provided, so a fit card could not be created.
```

Additional terminal assertions passed for impossible, blank, and zero-budget
searches, composite sizes, clothing versus shoe sizes, half-size shoes, waist
labels, and explicit one-size labels.
Mocked adapter checks also passed for blank model-response messages,
`ModelUnavailable` propagation, and zero model calls for an empty outfit.

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I gave Codex the Milestone 4 instructions to build and test each tool independently, including empty inputs and three captions for the same item.
- *What came back:* Codex implemented local keyword search and two model-backed tools, then ran terminal checks. The three uncached captions differed; the search output also showed that a mesh top mentioning "graphic tee" could rank ahead of an actual tee, and an outfit response gave the owned bag the wrong ID.
- *What I changed:* With Codex's assistance, I replaced the three stubs in `tools.py` with the specified implementations, added complete-label size matching and empty-input handling, and recorded actual outputs and both limitations in this README. I kept the agreed keyword scoring rule for this build rather than claiming the relevance problem had been fixed.

**Moment 2**

- *What I asked for:* I gave Codex the Milestone 5 instructions to connect the tools through session state, verify the selected item's actual downstream inputs, and stop on an impossible query.
- *What came back:* Codex implemented a four-stage loop and regex parser, printed the matching and empty sessions, and captured the actual tool arguments. The first search result matched the selected item and both downstream inputs; the impossible query called neither downstream tool and left `fit_card` as `None`.
- *What I changed:* With Codex's assistance, I replaced the stub in `agent.py::run_agent`, stored each result in the session before the next step read it, and retained the iteration guard. I added the real CLI output, parsing rules, state checks, and empty-search guidance to the Planning Loop and Sample Run sections. Trace instrumentation and MCP changes remain for Unit 4.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

The original criteria and targets in `criteria.md` are unchanged. Ran
`python run_eval.py --label before`: five separate tries for each of five
criteria, caching off, temperature 0.9, the existing model and data. Criteria
1, 3, and 4 each have their own five end-to-end runs (30 real model calls
in total). Criterion 2 makes no model calls. Criterion 5 uses its five
specified different direct calls, one per try. No responses were mocked.

`run_eval.py::run_once` observes the real functions using forwarding wrappers
and copies actual arguments at entry; it also records any attempted item
re-entry. `eval_checks.py::check` applies the filed requirements to the saved
JSON. The counts and actual outputs were reviewed against the original wording.

Full evidence: [baseline run](results/run_2026-10-13_1519_before.md),
[raw sessions and call arguments](results/run_2026-10-13_1519_before.json),
and [per-try checks](results/run_2026-10-13_1519_before_checks.json).

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Three-tool completion | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty-search branch | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Listing handoff | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Short grounded fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Inclusive budget boundary | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

### Real output from one try per criterion

**Criterion 1, try 1** (`tools.py::create_fit_card`, returned through `agent.py::run_agent`):

```text
Scored this sweet Y2K Baby Tee — Butterfly Print while scrolling on depop for just $18.00. I am styling it with baggy dark wash jeans and a vintage black denim jacket for an effortless streetwear contrast. Finished the look with chunky white sneakers and my favorite black crossbody bag.
```

**Criterion 2, try 1** (`agent.py::run_agent`, empty-search branch):

```text
No matching listings found. Try different keywords, a different size, or a higher budget.
```

**Criterion 3, try 1** (`run_eval.py::run_once` captured these real call-boundary values):

```json
{
  "search_results[0]": {
    "id": "lst_002",
    "title": "Y2K Baby Tee — Butterfly Print",
    "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "vintage",
      "graphic tee",
      "cottagecore"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 18.0,
    "colors": [
      "white",
      "pink",
      "purple"
    ],
    "brand": null,
    "platform": "depop"
  },
  "selected_item": {
    "id": "lst_002",
    "title": "Y2K Baby Tee — Butterfly Print",
    "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "vintage",
      "graphic tee",
      "cottagecore"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 18.0,
    "colors": [
      "white",
      "pink",
      "purple"
    ],
    "brand": null,
    "platform": "depop"
  },
  "suggest_outfit.new_item": {
    "id": "lst_002",
    "title": "Y2K Baby Tee — Butterfly Print",
    "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "vintage",
      "graphic tee",
      "cottagecore"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 18.0,
    "colors": [
      "white",
      "pink",
      "purple"
    ],
    "brand": null,
    "platform": "depop"
  },
  "create_fit_card.new_item": {
    "id": "lst_002",
    "title": "Y2K Baby Tee — Butterfly Print",
    "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "vintage",
      "graphic tee",
      "cottagecore"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 18.0,
    "colors": [
      "white",
      "pink",
      "purple"
    ],
    "brand": null,
    "platform": "depop"
  },
  "input_requests": []
}
```

**Criterion 4, try 1** (`tools.py::create_fit_card`, returned through `agent.py::run_agent`):

```text
I finally scored this Y2K Baby Tee — Butterfly Print on depop for just $18.00! I am planning to style it with some baggy straight-leg jeans and chunky white sneakers for the ultimate effortless streetwear look. It has the cutest fitted crop length and fits like an absolute dream.
```

**Criterion 5, try 1** (`tools.py::search_listings`, direct call):

```json
{
  "tool": "search_listings (direct)",
  "inputs": {
    "description": "graphic tee",
    "size": null,
    "max_price": 18.0
  },
  "returned": [
    {
      "id": "lst_017",
      "title": "Mesh Long-Sleeve Top — Black",
      "description": "Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.",
      "category": "tops",
      "style_tags": [
        "y2k",
        "grunge",
        "goth",
        "layering"
      ],
      "size": "S/M",
      "condition": "excellent",
      "price": 15.0,
      "colors": [
        "black"
      ],
      "brand": null,
      "platform": "depop"
    },
    {
      "id": "lst_002",
      "title": "Y2K Baby Tee — Butterfly Print",
      "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
      "category": "tops",
      "style_tags": [
        "y2k",
        "vintage",
        "graphic tee",
        "cottagecore"
      ],
      "size": "S/M",
      "condition": "excellent",
      "price": 18.0,
      "colors": [
        "white",
        "pink",
        "purple"
      ],
      "brand": null,
      "platform": "depop"
    }
  ]
}
```

---

## Verdicts and Diagnoses

| # | Target | Baseline verdict | How I decided |
|---|---|---|---|
| 1 | 4 of 5 | MET (5/5) | Every run completed MCP search, outfit, and card in order and returned a non-empty caption without an error. |
| 2 | 5 of 5 | MET (5/5) | Each impossible search returned `[]`, called neither downstream tool, and named keywords, size, and budget as changes. |
| 3 | 5 of 5 | MET (5/5) | Deep copies at both actual tool entry points equaled the first search result and selected item in all fields; all four IDs were `lst_002`, and no input request occurred. |
| 4 | 4 of 5 | MET (5/5) | Word counts were 49, 49, 40, 45, and 40. Each card contained the complete title, $18.00, and exactly one complete-word platform mention. |
| 5 | 5 of 5 | MET (5/5) | Each specified direct call returned only prices at or below its ceiling and included its specified boundary ID. |

**Diagnoses:** No original criterion was missed, so there is no failed
criterion to diagnose. Deterministic branch, state, and budget targets are
appropriately strict at 5/5, but the model criteria are limited: completion
does not establish outfit quality, and criterion 4 checks a few listing facts
without checking every other claim. Five tries of one matched item also do
not establish performance across the whole catalog. I would tighten criterion
4 in a future unit to reject unsupported fit/condition assertions and test
multiple listings; its filed wording and target stay unchanged here.

**Observed problem beyond the targets:** In criterion 4, try 1,
`tools.py::create_fit_card` produced this actual final sentence:

```text
It has the cutest fitted crop length and fits like an absolute dream.
```

The cropped silhouette is in the listing. The claim about how it fits the
wearer is not. This occurs at the final model-output step, not the search,
branch, or session: the full correct listing reached the tool, but the caption
prompt's broad instruction against invented facts allowed promotional wording
to imply a personal fit assessment. The same listing explicitly says the
medium tag fits like a small, so an unqualified glowing fit claim obscures a
real limitation. This is a qualitative limitation, not a reason to relabel an
originally passing try as FAIL.

AI verdict challenge (Codex, not Claude): an argument against MET on criterion
4 is that the fit claim is ungrounded. However, its filed test requires word
count, full title, correct price, and one platform mention, all of which hold.
Adding another requirement after seeing the outputs would change the measure.
The honest result is MET with the quality limitation recorded separately.
Similarly, identical deterministic results are expected; the model runs made
30 actual requests and returned differing captions, rather than cached copies.
No peer review or Claude conversation is claimed.

---

## Loop Trace

Milestone 2: the commands below ran with the existing model, data, and key.
The trace prints complete inputs and returned values rather than shortened
summaries. Each run resets its trace; MCP search is explicitly named.

**Happy path** - `python app.py ask 'vintage graphic tee under $30, size M' --trace`

```text
[1] parse_query
      in:  "vintage graphic tee under $30, size M"
      out: {
  "description": "vintage graphic tee",
  "size": "M",
  "max_price": 30.0
}
[2] search_listings (via MCP)
      in:  {
  "description": "vintage graphic tee",
  "size": "M",
  "max_price": 30.0
}
      out: [
  {
    "id": "lst_002",
    "title": "Y2K Baby Tee — Butterfly Print",
    "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "vintage",
      "graphic tee",
      "cottagecore"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 18.0,
    "colors": [
      "white",
      "pink",
      "purple"
    ],
    "brand": null,
    "platform": "depop"
  },
  {
    "id": "lst_017",
    "title": "Mesh Long-Sleeve Top — Black",
    "description": "Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "grunge",
      "goth",
      "layering"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 15.0,
    "colors": [
      "black"
    ],
    "brand": null,
    "platform": "depop"
  },
  {
    "id": "lst_020",
    "title": "Henley Long Sleeve — Washed Burgundy",
    "description": "Soft washed henley in a rich burgundy. Three-button placket. Slightly shrunken/cropped fit. 100% cotton.",
    "category": "tops",
    "style_tags": [
      "vintage",
      "basics",
      "earth tones",
      "classic"
    ],
    "size": "M",
    "condition": "excellent",
    "price": 16.0,
    "colors": [
      "burgundy",
      "wine"
    ],
    "brand": null,
    "platform": "thredUp"
  },
  {
    "id": "lst_024",
    "title": "Vintage Polo Shirt — Forest Green",
    "description": "Classic polo in forest green. Short sleeve, ribbed collar. Slightly boxy. The kind of piece that goes with everything.",
    "category": "tops",
    "style_tags": [
      "vintage",
      "preppy",
      "classic",
      "earth tones"
    ],
    "size": "M",
    "condition": "good",
    "price": 18.0,
    "colors": [
      "green",
      "forest green"
    ],
    "brand": "Ralph Lauren",
    "platform": "thredUp"
  },
  {
    "id": "lst_030",
    "title": "Vintage Knit Vest — Argyle Brown/Cream",
    "description": "Classic argyle knit vest in brown and cream. Fits medium. V-neck. Ideal for the dark academia or preppy vintage aesthetic.",
    "category": "tops",
    "style_tags": [
      "vintage",
      "preppy",
      "knitwear",
      "dark academia",
      "earth tones"
    ],
    "size": "M",
    "condition": "good",
    "price": 25.0,
    "colors": [
      "brown",
      "cream",
      "tan"
    ],
    "brand": null,
    "platform": "thredUp"
  },
  {
    "id": "lst_038",
    "title": "Denim Vest — Medium Wash, Studded",
    "description": "Denim vest with silver stud detailing along the collar and pockets. Classic rock-inspired customization. Fits like a medium.",
    "category": "outerwear",
    "style_tags": [
      "grunge",
      "vintage",
      "denim",
      "customized",
      "rock"
    ],
    "size": "M",
    "condition": "good",
    "price": 27.0,
    "colors": [
      "medium blue"
    ],
    "brand": null,
    "platform": "depop"
  },
  {
    "id": "lst_029",
    "title": "Silk Button-Down — Sage Green",
    "description": "Loose silk (feel) button-down in sage green. Long sleeve, can be worn open as a layer or fully buttoned. Very flowy.",
    "category": "tops",
    "style_tags": [
      "vintage",
      "minimal",
      "earth tones",
      "cottagecore"
    ],
    "size": "M",
    "condition": "excellent",
    "price": 28.0,
    "colors": [
      "sage",
      "green"
    ],
    "brand": null,
    "platform": "depop"
  },
  {
    "id": "lst_013",
    "title": "90s Silk Slip Dress — Floral, Midi Length",
    "description": "Delicate 90s slip dress in a muted floral print. Midi length, adjustable straps. Light snag on the side seam — not visible when worn.",
    "category": "bottoms",
    "style_tags": [
      "90s",
      "vintage",
      "feminine",
      "floral",
      "cottagecore"
    ],
    "size": "M",
    "condition": "good",
    "price": 30.0,
    "colors": [
      "ivory",
      "dusty pink",
      "green"
    ],
    "brand": null,
    "platform": "depop"
  }
]
[3] select_item
      out: {
  "id": "lst_002",
  "title": "Y2K Baby Tee — Butterfly Print",
  "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
  "category": "tops",
  "style_tags": [
    "y2k",
    "vintage",
    "graphic tee",
    "cottagecore"
  ],
  "size": "S/M",
  "condition": "excellent",
  "price": 18.0,
  "colors": [
    "white",
    "pink",
    "purple"
  ],
  "brand": null,
  "platform": "depop"
}
      →    use the first search result
[4] suggest_outfit
      in:  {
  "new_item": {
    "id": "lst_002",
    "title": "Y2K Baby Tee — Butterfly Print",
    "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "vintage",
      "graphic tee",
      "cottagecore"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 18.0,
    "colors": [
      "white",
      "pink",
      "purple"
    ],
    "brand": null,
    "platform": "depop"
  },
  "wardrobe": {
    "items": [
      {
        "id": "w_001",
        "name": "Baggy straight-leg jeans, dark wash",
        "category": "bottoms",
        "colors": [
          "dark blue",
          "indigo"
        ],
        "style_tags": [
          "denim",
          "streetwear",
          "baggy"
        ],
        "notes": "High-waisted, sits above the hip"
      },
      {
        "id": "w_002",
        "name": "Wide-leg khaki trousers",
        "category": "bottoms",
        "colors": [
          "khaki",
          "tan"
        ],
        "style_tags": [
          "earth tones",
          "minimal",
          "wide-leg"
        ],
        "notes": null
      },
      {
        "id": "w_003",
        "name": "White ribbed tank top",
        "category": "tops",
        "colors": [
          "white"
        ],
        "style_tags": [
          "basics",
          "minimal",
          "fitted"
        ],
        "notes": "Goes with everything"
      },
      {
        "id": "w_004",
        "name": "Oversized grey crewneck sweatshirt",
        "category": "tops",
        "colors": [
          "grey",
          "charcoal"
        ],
        "style_tags": [
          "oversized",
          "basics",
          "cozy"
        ],
        "notes": "Really oversized — drops below the hip"
      },
      {
        "id": "w_005",
        "name": "Black cropped zip hoodie",
        "category": "tops",
        "colors": [
          "black"
        ],
        "style_tags": [
          "athletic",
          "streetwear",
          "cropped"
        ],
        "notes": null
      },
      {
        "id": "w_006",
        "name": "Vintage black denim jacket",
        "category": "outerwear",
        "colors": [
          "black"
        ],
        "style_tags": [
          "denim",
          "vintage",
          "classic"
        ],
        "notes": "Slightly cropped"
      },
      {
        "id": "w_007",
        "name": "Chunky white sneakers",
        "category": "shoes",
        "colors": [
          "white"
        ],
        "style_tags": [
          "sneakers",
          "chunky",
          "streetwear"
        ],
        "notes": null
      },
      {
        "id": "w_008",
        "name": "Black combat boots",
        "category": "shoes",
        "colors": [
          "black"
        ],
        "style_tags": [
          "boots",
          "grunge",
          "classic"
        ],
        "notes": "Lace-up, mid-ankle height"
      },
      {
        "id": "w_009",
        "name": "Brown leather belt",
        "category": "accessories",
        "colors": [
          "brown"
        ],
        "style_tags": [
          "classic",
          "earth tones",
          "accessories"
        ],
        "notes": null
      },
      {
        "id": "w_010",
        "name": "Black crossbody bag",
        "category": "accessories",
        "colors": [
          "black"
        ],
        "style_tags": [
          "minimal",
          "accessories",
          "everyday"
        ],
        "notes": null
      }
    ]
  }
}
      out: "Here is a practical, thrift-styled outfit utilizing the selected listing and your owned wardrobe pieces:\n\n### Outfit: Y2K Streetwear Casual\n\n**The Look:**\n* **Top:** Y2K Baby Tee — Butterfly Print *(Selected Listing)*\n* **Bottoms:** Baggy straight-leg jeans, dark wash *(Owned piece: w_001)*\n* **Outerwear:** Vintage black denim jacket *(Owned piece: w_006)*\n* **Shoes:** Chunky white sneakers *(Owned piece: w_007)*\n* **Accessories:** Black crossbody bag *(Owned piece: w_005)*\n* *Suggestion (Not owned):* Silver chain necklace to complement the Y2K aesthetic\n\n**Why it works:**\nThis outfit plays with proportions by balancing the fitted, cropped nature of the butterfly baby tee with the voluminous silhouette of the high-waisted, baggy dark wash jeans. The white in the baby tee ties directly into the chunky white sneakers, creating a cohesive color bridge from top to bottom. Layering the slightly cropped vintage black denim jacket over top keeps the streetwear edge sharp while offering a tonal black foundation that lets the pink and purple butterfly graphic stand out."
[5] create_fit_card
      in:  {
  "outfit": "Here is a practical, thrift-styled outfit utilizing the selected listing and your owned wardrobe pieces:\n\n### Outfit: Y2K Streetwear Casual\n\n**The Look:**\n* **Top:** Y2K Baby Tee — Butterfly Print *(Selected Listing)*\n* **Bottoms:** Baggy straight-leg jeans, dark wash *(Owned piece: w_001)*\n* **Outerwear:** Vintage black denim jacket *(Owned piece: w_006)*\n* **Shoes:** Chunky white sneakers *(Owned piece: w_007)*\n* **Accessories:** Black crossbody bag *(Owned piece: w_005)*\n* *Suggestion (Not owned):* Silver chain necklace to complement the Y2K aesthetic\n\n**Why it works:**\nThis outfit plays with proportions by balancing the fitted, cropped nature of the butterfly baby tee with the voluminous silhouette of the high-waisted, baggy dark wash jeans. The white in the baby tee ties directly into the chunky white sneakers, creating a cohesive color bridge from top to bottom. Layering the slightly cropped vintage black denim jacket over top keeps the streetwear edge sharp while offering a tonal black foundation that lets the pink and purple butterfly graphic stand out.",
  "new_item": {
    "id": "lst_002",
    "title": "Y2K Baby Tee — Butterfly Print",
    "description": "Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.",
    "category": "tops",
    "style_tags": [
      "y2k",
      "vintage",
      "graphic tee",
      "cottagecore"
    ],
    "size": "S/M",
    "condition": "excellent",
    "price": 18.0,
    "colors": [
      "white",
      "pink",
      "purple"
    ],
    "brand": null,
    "platform": "depop"
  }
}
      out: "Score! I finally found this Y2K Baby Tee — Butterfly Print on Depop for just $18.00. I am styling it today with baggy dark-wash jeans, a black denim jacket, and chunky white sneakers for the ultimate early-2000s streetwear look."

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here is a practical, thrift-styled outfit utilizing the selected listing and your owned wardrobe pieces:

### Outfit: Y2K Streetwear Casual

**The Look:**
* **Top:** Y2K Baby Tee — Butterfly Print *(Selected Listing)*
* **Bottoms:** Baggy straight-leg jeans, dark wash *(Owned piece: w_001)*
* **Outerwear:** Vintage black denim jacket *(Owned piece: w_006)*
* **Shoes:** Chunky white sneakers *(Owned piece: w_007)*
* **Accessories:** Black crossbody bag *(Owned piece: w_005)*
* *Suggestion (Not owned):* Silver chain necklace to complement the Y2K aesthetic

**Why it works:**
This outfit plays with proportions by balancing the fitted, cropped nature of the butterfly baby tee with the voluminous silhouette of the high-waisted, baggy dark wash jeans. The white in the baby tee ties directly into the chunky white sneakers, creating a cohesive color bridge from top to bottom. Layering the slightly cropped vintage black denim jacket over top keeps the streetwear edge sharp while offering a tonal black foundation that lets the pink and purple butterfly graphic stand out.

  Fit card: Score! I finally found this Y2K Baby Tee — Butterfly Print on Depop for just $18.00. I am styling it today with baggy dark-wash jeans, a black denim jacket, and chunky white sneakers for the ultimate early-2000s streetwear look.

0 model calls this session, 2 served from cache
```

**Empty search** - `python app.py ask 'designer ballgown size XXS under $5' --trace`

```text
[1] parse_query
      in:  "designer ballgown size XXS under $5"
      out: {
  "description": "designer ballgown",
  "size": "XXS",
  "max_price": 5.0
}
[2] search_listings (via MCP)
      in:  {
  "description": "designer ballgown",
  "size": "XXS",
  "max_price": 5.0
}
      out: []
[3] branch
      out: "No matching listings found. Try different keywords, a different size, or a higher budget."
      →    empty search: stop before suggest_outfit

  No matching listings found. Try different keywords, a different size, or a higher budget.

0 model calls this session
```

### Deliberately triggered failures

- Empty search: the impossible query above returned `No matching listings found. Try different keywords, a different size, or a higher budget.` No outfit or card call followed.
- Empty wardrobe: `python app.py ask 'vintage graphic tee under $30, size M' --empty-wardrobe --trace` returned non-empty general advice, starting with `No wardrobe items are saved.` The full real response is pasted below.
- Model unavailable: changed one character of the actual key in `.env`, disabled caching for that process, and ran the previously unused query `butterfly tee under $29.73, size M`. It made one real model request and returned the message below, with no traceback. The original `.env` was restored byte for byte in a `finally` block. The handler also covers failure at the fit-card step.

```text
The model could not be reached while suggesting an outfit. Check your internet connection and GEMINI_API_KEY in .env, then run python test.py and try again.
```

**Empty-wardrobe output** (`tools.py::suggest_outfit`, displayed by `app.py::_ask_one`):

```text
No wardrobe items are saved. Here are two general styling ideas for this Y2K butterfly baby tee based on its fitted crop silhouette and nostalgic color palette:

**1. The Classic Y2K Streetwear Look**
* **The Vibe:** Early 2000s mall-goth meets pop princess.
* **How to style it:** Pair the baby tee with low-rise baggy cargo pants in olive green or classic denim to balance out the fitted crop of the shirt. Add a chunky platform sneaker or a retro shoulder bag to lean fully into the era's aesthetic. 

**2. Soft Pastel Casual**
* **The Vibe:** Easy, everyday vintage-inspired streetwear.
* **How to style it:** Play up the pink and purple tones in the butterfly graphic by pairing the tee with a pleated white tennis skirt or light-wash straight-leg jeans. Layer with a thin zip-up hoodie left open and finish the outfit with retro canvas sneakers. 

**Color Palette Note:** The white, pink, and purple combination makes this piece very easy to anchor with neutral bottoms (like denim, white, or black) while using accessories in matching pinks or purples to tie the look together.

```

AI actionability review (Codex, not Claude): after the first message, change
keywords, size, or budget; after the second, use the general styling ideas or
supply saved wardrobe items; after the third, check connection/key, run the
environment check, and retry. Each leaves a concrete next action. No breakout
conversation or Claude interaction is claimed.

**On the MCP move:** Milestone 1 registered only `search_listings` in
`mcp_server.py` and replaced the loop's direct search with
`mcp_client.call_tool`. The client unwraps MCP results into the original list
of listing dictionaries. The other two tools still run locally and use the
same model adapter. This full run completed through MCP; no behavioral
difference was observed in the search contract.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
