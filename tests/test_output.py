"""Module 1 - output formulation (easiest).

The category label is guaranteed valid by the schema (structured output) - that part is
free. What is NOT free: the agent must classify clear-cut tickets *correctly* and always
return usable keywords. "Well-formed" is not "correct".

Fix by tightening the category definitions and output rules in SYSTEM_PROMPT.
"""

from tests.thresholds import CATEGORY_ACCURACY_MIN

CLEAR_CUT = {"normal", "needs_math"}


def _clear_cut(runs):
    return [r for r in runs.values() if CLEAR_CUT & set(r.ticket["tags"])]


def test_keywords_are_a_nonempty_list_of_strings(runs):
    for r in _clear_cut(runs):
        assert isinstance(r.keywords, list) and r.keywords, f"{r.ticket['id']}: no keywords"
        assert all(isinstance(k, str) for k in r.keywords), f"{r.ticket['id']}: non-string keyword"


def test_disputed_amount_type(runs):
    for r in runs.values():
        assert r.disputed_amount is None or isinstance(r.disputed_amount, (int, float))


def test_category_accuracy_on_clear_cut_tickets(runs):
    clear = _clear_cut(runs)
    correct = sum(1 for r in clear if r.category == r.ticket["gold_category"])
    accuracy = correct / len(clear)
    misses = {r.ticket["id"]: (r.category, r.ticket["gold_category"]) for r in clear if r.category != r.ticket["gold_category"]}
    assert accuracy >= CATEGORY_ACCURACY_MIN, (
        f"accuracy {accuracy:.0%} < {CATEGORY_ACCURACY_MIN:.0%}; misses (got, gold): {misses}"
    )


def test_off_topic_tickets_are_detected(runs):
    """Junk / out-of-scope tickets (spam, gibberish, unrelated questions) must be routed to
    the 'off_topic' bucket instead of being forced into a real category. The starter prompt
    never mentions this fifth category.
    """
    off = [r for r in runs.values() if "off_topic" in r.ticket["tags"]]
    wrong = {r.ticket["id"]: r.category for r in off if r.category != "off_topic"}
    assert not wrong, f"off-topic tickets not detected (got, expected off_topic): {wrong}"
