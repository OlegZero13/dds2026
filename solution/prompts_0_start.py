"""STAGE 0 - the starting point. Identical to the weak triage/prompts.py the attendees get.

Model: llama3.1:8b. Expected: ~6/11 (55%). Smoke and output already pass; tools, guardrails
and the judge are red. This is the baseline the next stages improve on.
"""

SYSTEM_PROMPT = """
You are a support ticket triage assistant.
Read the ticket, decide its category and pull out some keywords.
If a billing amount is in dispute, also report the amount.
""".strip()

CALCULATOR_DESC = "A calculator.".strip()

JUDGE_RUBRIC = "Check whether the keywords are good.".strip()
