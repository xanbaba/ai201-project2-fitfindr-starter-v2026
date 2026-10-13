"""Transparent checks of the unchanged criteria, applied to saved real runs.

This never calls a tool or model. Inspect the JSON and these checks together.
Usage: python eval_checks.py results/run_..._before.json
"""
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

NAMES = ["Three-tool completion", "Empty-search branch", "Listing handoff",
         "Short grounded fit card", "Inclusive budget boundary"]
TARGETS = [4, 5, 5, 4, 5]


def check(number, record):
    session = record.get("session") or {}
    calls = record["calls"]
    names = [call["tool"] for call in calls]
    item = session.get("selected_item") or {}
    card = session.get("fit_card") or ""
    if record.get("crashed"):
        return False, {"crashed": record["crashed"]}
    if number == 1:
        facts = {"tool_order": names, "returned_fit_card": bool(card.strip()),
                 "stopped": bool(session.get("error")),
                 "fallback": card == "No fit card was generated. Try again."}
        return (names == ["search_listings (via MCP)", "suggest_outfit", "create_fit_card"]
                and all("returned" in call for call in calls)
                and facts["returned_fit_card"] and not facts["stopped"] and not facts["fallback"]), facts
    if number == 2:
        message = session.get("error") or ""
        facts = {"tool_order": names, "search_empty": session.get("search_results") == [],
                 "message": message, "names_next_action": any(
                     word in message.lower() for word in ("keywords", "size", "budget"))}
        return (facts["search_empty"] and names == ["search_listings (via MCP)"]
                and facts["names_next_action"]), facts
    if number == 3:
        outfit = next((call for call in calls if call["tool"] == "suggest_outfit"), {})
        caption = next((call for call in calls if call["tool"] == "create_fit_card"), {})
        results = session.get("search_results") or []
        dictionaries = [results[0] if results else None, item or None,
                        outfit.get("inputs", {}).get("new_item"),
                        caption.get("inputs", {}).get("new_item")]
        equal = bool(dictionaries[0]) and all(value == dictionaries[0] for value in dictionaries)
        facts = {"all_four_dictionaries_equal": equal,
                 "ids": [value.get("id") if value else None for value in dictionaries],
                 "input_requests": record["input_requests"]}
        return equal and not record["input_requests"], facts
    if number == 4:
        # A sentence-ending period after $18.00 is punctuation, not part of
        # the amount. Capture the whole decimal before comparing its value.
        prices = re.findall(r"\$\s*(\d+(?:\.\d+)?)", card)
        platform = item.get("platform", "")
        facts = {"word_count": len(card.split()),
                 "complete_title_present": bool(item) and item["title"].lower() in card.lower(),
                 "correct_dollar_price": bool(item) and any(
                     Decimal(price) == Decimal(str(item["price"])) for price in prices),
                 "platform_occurrences": len(re.findall(r"\b" + re.escape(platform) + r"\b", card, re.I)) if platform else 0}
        return (not session.get("error") and 25 <= facts["word_count"] <= 90
                and facts["complete_title_present"] and facts["correct_dollar_price"]
                and facts["platform_occurrences"] == 1), facts
    case = record["direct_case"]
    results = session.get("search_results") or []
    facts = {"case": case, "returned_ids": [item["id"] for item in results],
             "returned_prices": [item["price"] for item in results],
             "all_within_budget": all(item["price"] <= case["max_price"] for item in results),
             "boundary_present": any(item["id"] == case["boundary_id"] for item in results)}
    return bool(results) and facts["all_within_budget"] and facts["boundary_present"], facts


def score(data):
    scored = []
    for row in data["rows"]:
        number = row["scenario"]["criterion"]
        checks = [check(number, record) for record in row["tries"]]
        passed = sum(result for result, _ in checks)
        scored.append({"criterion": number, "name": NAMES[number-1],
                       "target": TARGETS[number-1], "passes": passed,
                       "verdict": ("MET" if passed >= TARGETS[number-1] else "MISSED") + f" ({passed}/5)",
                       "tries": [{"pass": result, "facts": facts} for result, facts in checks]})
    return scored


def table(scored):
    lines = ["| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |",
             "|---|---|---|---|---|---|---|---|"]
    for row in scored:
        cells = " | ".join("PASS" if trial["pass"] else "FAIL" for trial in row["tries"])
        lines.append(f"| {row['criterion']}. {row['name']} | {row['target']} of 5 | {cells} | {row['verdict']} |")
    return "\n".join(lines)


if __name__ == "__main__":
    path = Path(sys.argv[1])
    scored = score(json.loads(path.read_text(encoding="utf-8")))
    path.with_name(path.stem + "_checks.json").write_text(
        json.dumps(scored, ensure_ascii=False, indent=2), encoding="utf-8")
    print(table(scored))
    for row in scored:
        for i, trial in enumerate(row["tries"], 1):
            print(f"Criterion {row['criterion']}, try {i}: {trial}")
