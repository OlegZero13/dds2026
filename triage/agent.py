"""The triage agent. Wires the model, the calculator tool and the tunable prompt.

A fresh agent is built per run so edits to prompts.py are picked up on the next
`uv run pytest`. `classify()` returns the full RunOutput so tests can inspect both
the structured `content` (a TriageResult) and the `tools` actually called.
"""

from __future__ import annotations

from agno.agent import Agent

from triage.model import get_model
from triage.prompts import SYSTEM_PROMPT
from triage.schema import TriageResult
from triage.tools import calculator


def build_agent() -> Agent:
    return Agent(
        model=get_model(),
        tools=[calculator],
        instructions=SYSTEM_PROMPT,
        output_schema=TriageResult,
        parser_model=get_model(),
    )


def classify(ticket_text: str):
    """Run the agent on one ticket and return the RunOutput."""
    return build_agent().run(ticket_text)


def classify_summary(ticket_text: str) -> dict:
    """Run the agent and return a plain dict the web UI / scripts can render."""
    out = build_agent().run(ticket_text)
    tools = [
        {
            "name": getattr(t, "tool_name", None),
            "args": getattr(t, "tool_args", None),
            "result": getattr(t, "result", None),
        }
        for t in (out.tools or [])
    ]
    content = out.content
    if isinstance(content, TriageResult):
        return {
            "category": content.category,
            "keywords": list(content.keywords or []),
            "disputed_amount": content.disputed_amount,
            "tools": tools,
        }
    return {"category": None, "keywords": [], "disputed_amount": None, "tools": tools}
