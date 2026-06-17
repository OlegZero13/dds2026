"""Model wiring.

The agent runs on OLLAMA_HOST / MODEL_ID. The DeepEval judge can use a SEPARATE,
stronger model via JUDGE_OLLAMA_HOST / JUDGE_MODEL_ID — handy for testing a weak local
agent while grading with a reliable judge. Both judge vars default to the agent's, so by
default one model backs everything (no API keys, no signups).
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_ID = os.environ.get("MODEL_ID", "llama3.1:8b")

# Judge defaults to the agent's model/host; override to grade with a stronger model.
JUDGE_OLLAMA_HOST = os.environ.get("JUDGE_OLLAMA_HOST", OLLAMA_HOST)
JUDGE_MODEL_ID = os.environ.get("JUDGE_MODEL_ID", MODEL_ID)


def get_model():
    """Agno model used by the agent (and its parser step).

    temperature=0 (plus a fixed seed) keeps the agent as reproducible as possible, so the
    scoreboard reflects your prompt rather than the luck of the draw.
    """
    from agno.models.ollama import Ollama

    return Ollama(id=MODEL_ID, host=OLLAMA_HOST, options={"temperature": 0, "seed": 42})


def get_judge():
    """DeepEval model used as the LLM-as-judge.

    Uses JUDGE_MODEL_ID / JUDGE_OLLAMA_HOST, which default to the agent's. Set them to a
    stronger model to grade a weak agent reliably.
    """
    from deepeval.models import OllamaModel

    return OllamaModel(model=JUDGE_MODEL_ID, base_url=JUDGE_OLLAMA_HOST, temperature=0)
