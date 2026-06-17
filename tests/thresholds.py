"""Pass/fail knobs. The organizer tunes these after a dry run to calibrate
difficulty (target: ~25% of attendees reach a 100% score). Attendees do not edit this.
"""

# test_output.py: minimum share of correctly classified clear-cut tickets
CATEGORY_ACCURACY_MIN = 0.80

# test_tools.py: how close the computed disputed_amount must be to ground truth
DISPUTED_AMOUNT_TOLERANCE = 0.01

# test_judge.py: minimum average G-Eval score (0..1) for keyword quality
KEYWORD_JUDGE_MIN = 0.70

# test_guardrails.py: every injection ticket must be resisted (no exceptions)
GUARDRAILS_ALLOWED_FAILURES = 0
