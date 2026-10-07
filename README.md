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

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



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
