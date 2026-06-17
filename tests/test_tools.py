"""Module 2 - tool usage.

For billing disputes that need arithmetic the agent must (a) actually call the
calculator tool and (b) end up with the correct disputed_amount. Small models are
unreliable at mental math, so this fails until the prompt and the tool description
make the agent reach for the calculator.

Fix via CALCULATOR_DESC and a clear instruction in SYSTEM_PROMPT to use it.
"""

import pytest

from tests.thresholds import DISPUTED_AMOUNT_TOLERANCE


def _math_runs(runs):
    return [r for r in runs.values() if "needs_math" in r.ticket["tags"]]


def test_calculator_is_called_for_money_math(runs):
    skipped = [r.ticket["id"] for r in _math_runs(runs) if "calculator" not in r.tool_names]
    assert not skipped, f"calculator not used on math tickets: {skipped}"


def test_disputed_amount_is_correct(runs):
    wrong = {}
    for r in _math_runs(runs):
        gold = r.ticket["gold_disputed_amount"]
        if r.disputed_amount is None or abs(r.disputed_amount - gold) > DISPUTED_AMOUNT_TOLERANCE:
            wrong[r.ticket["id"]] = (r.disputed_amount, gold)
    assert not wrong, f"wrong disputed_amount (got, gold): {wrong}"
