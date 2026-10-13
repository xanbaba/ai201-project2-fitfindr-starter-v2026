"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

# Criterion 5 deliberately uses five DIFFERENT direct calls, as filed in
# criteria.md. The runner chooses one case per try, rather than five per try.
BUDGET_CASES = [
    {"description": "graphic tee", "max_price": 18.0, "boundary_id": "lst_002"},
    {"description": "graphic tee", "max_price": 24.0, "boundary_id": "lst_006"},
    {"description": "band tee", "max_price": 19.0, "boundary_id": "lst_033"},
    {"description": "denim jacket", "max_price": 42.0, "boundary_id": "lst_007"},
    {"description": "silk slip dress", "max_price": 30.0, "boundary_id": "lst_013"},
]

SCENARIOS = [
    {"name": "matching query completes", "query": "vintage graphic tee under $30",
     "wardrobe": "example", "criterion": 1},
    {"name": "impossible query stops early", "query": "designer ballgown size XXS under $5",
     "wardrobe": "example", "criterion": 2},
    {"name": "selected listing reaches both tools unchanged",
     "query": "vintage graphic tee under $30, size M", "wardrobe": "example", "criterion": 3},
    {"name": "short grounded fit card", "query": "vintage graphic tee under $30, size M",
     "wardrobe": "example", "criterion": 4},
    {"name": "inclusive budget boundaries", "query": "five direct cases from criteria.md",
     "wardrobe": "example", "criterion": 5, "kind": "direct_search"},
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
