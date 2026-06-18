"""STAGE 1 - output formulation (cumulative). Model: llama3.1:8b.

Builds on the weak start by spelling out the four categories and demanding real keywords.
This locks the output contract (valid category, non-empty keywords) and improves keyword
quality. Tools, guardrails and the judge are still weak/red - that comes next.
"""

SYSTEM_PROMPT = """
Classify the tickets.
""".strip()

CALCULATOR_DESC = "A calculator.".strip()

JUDGE_RUBRIC = "Check whether the keywords are good.".strip()
