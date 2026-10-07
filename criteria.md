# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
Two steps depend on model responses, which may be empty or fail even when the
local search finds an item. Four of five requires reliable end-to-end behavior
while allowing one unsuccessful model-dependent run; five of five would also
require the external service to succeed every time.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This path depends on a deterministic empty-list check and should make no model
requests. Five of five is appropriate because one attempt to style a nonexistent
item means the branch is unsafe, rather than normal variation in model wording.

---

## 3. The selected listing reaches both downstream tools unchanged

Given the query `vintage graphic tee under $30, size M` and the example
wardrobe, the full listing dictionary in `session["search_results"][0]`,
`session["selected_item"]`, the actual `new_item` argument received by
`suggest_outfit`, and the actual `new_item` argument received by
`create_fit_card` must all be equal, including their `id`, with no second
request for the user to enter the item — in 5 of 5 tries. A missing downstream
call or a missing selected item counts as a failure.

**Why this target:**
Passing a stored dictionary between functions is controlled by the code, not
by model wording, so all five runs must preserve it. Comparing all fields at
the actual call boundaries catches an altered price or size even if the ID
still matches; comparing only the final session would miss that mistake.

---

## 4. The fit card is short and grounded in the selected listing

Given the query `vintage graphic tee under $30, size M` and the example
wardrobe, the returned `session["fit_card"]` must contain 25–90
whitespace-separated words, the selected listing's complete title
(case-insensitive), its correct dollar price (for example, `$18` or `$18.00`
for a price of 18.0), and its platform name exactly once as a complete word
(case-insensitive) — in at least 4 of 5 tries with response caching disabled.
A crash, early stop, or missing fit card counts as a failure.

**Why this target:**
The length range allows a few conversational sentences while preventing a
long product description. The title, price, and platform make the find
identifiable; four of five allows one model formatting miss without accepting
captions that routinely omit or invent listing facts.

---

## 5. Search respects the budget and includes its boundary

For five direct `search_listings` calls with `size=None`, using respectively
(`description`, `max_price`, expected boundary item ID):
(`graphic tee`, 18.0, `lst_002`), (`graphic tee`, 24.0, `lst_006`),
(`band tee`, 19.0, `lst_033`), (`denim jacket`, 42.0, `lst_007`), and
(`silk slip dress`, 30.0, `lst_013`), every returned listing must have
`price <= max_price` and the expected boundary item must be present —
5 of 5 calls. An empty result or an exception counts as a failure.

**Why this target:**
The budget is a hard constraint applied to numeric local data, so model
variation is no reason to exceed it. Requiring the known item priced exactly
at each ceiling also catches an exclusive comparison or a search that returns
nothing just to avoid over-budget results; five cases cover multiple prices
and item descriptions.

---

## Testability review — procedure only, no results

The following procedures check whether each criterion can be measured from
its wording. The criteria have not been evaluated against the agent.

1. Use a query known from the data to have a match and the example wardrobe.
   Run it five times, record the three tool calls, and count runs that return
   a fit card. At least four must complete all three calls.
2. Use a query with no matching listing and run it five times. Capture calls
   to `suggest_outfit` and inspect the returned message. All five must stop
   without calling that tool and name something the user could change.
3. Run the stated query five times. Capture a deep copy of each tool's actual
   `new_item` argument at entry, then compare those copies to the first search
   result and selected item. Record any user-input request. All four listing
   dictionaries must agree in every run, with both calls present and no re-entry.
4. Disable caching and run the stated query five times. For each fit card,
   count words using whitespace splitting, check the full title ignoring case,
   check a dollar amount equal to the selected price, and count complete-word
   occurrences of the platform name ignoring case. At least four cards must
   meet every requirement.
5. Make the five specified direct search calls. Inspect every returned price
   and check that each specified boundary ID is present in its result list.
   All five calls must satisfy both checks.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
