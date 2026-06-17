"""Module 0 - smoke. Green from the start: the agent runs and returns the schema.

This proves the plumbing works. It says nothing about whether the answers are *correct* —
that is what every other module is for.
"""

from triage.schema import TriageResult
from triage.agent import classify


def test_agent_returns_structured_output():
    out = classify("My app keeps crashing on startup.")
    assert isinstance(out.content, TriageResult)


def test_output_has_required_fields():
    out = classify("Please add a dark mode.")
    result = out.content
    assert isinstance(result.category, str) and result.category
    assert isinstance(result.keywords, list)
