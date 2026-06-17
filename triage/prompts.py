"""The three tunable surfaces of the workshop.

This is the ONLY file you are meant to edit. Improve the three strings below to
make the test suite pass and raise your production-readiness score. Do NOT edit
the tests, the schema, or the dataset.

  1. SYSTEM_PROMPT   - how the agent classifies tickets and uses its tool
  2. CALCULATOR_DESC - what the calculator tool is and when to call it
  3. JUDGE_RUBRIC    - how the LLM judge grades the quality of keywords

Everything here starts deliberately weak. That is the point.
"""

# 1) Agent system prompt -------------------------------------------------------
SYSTEM_PROMPT = """
You are a support ticket triage assistant.
Read the ticket, decide its category and pull out some keywords.
If a billing amount is in dispute, also report the amount.
""".strip()


# 2) Calculator tool description ----------------------------------------------
CALCULATOR_DESC = "A calculator.".strip()


# 3) LLM-as-judge rubric (keyword quality) ------------------------------------
JUDGE_RUBRIC = "Check whether the keywords are good.".strip()
