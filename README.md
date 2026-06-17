# Testing Agentic Applications — Support-Ticket Triage

A hands-on workshop on **testing LLM agents**. You are given a working support-ticket
triage agent and a test suite that is mostly **red**. Your job: make it green by
improving prompts — not by editing the tests.

The agent reads a support ticket and returns:
- a **category**: `billing`, `technical`, `feature_request`, or `complaint`
- a list of **keywords**
- a **disputed_amount** for billing disputes (computed with a calculator tool)

It looks correct at a glance. The workshop asks: **how do we actually know?**

## Setup (Linux / macOS / Windows)

You only need [`uv`](https://docs.astral.sh/uv/) and the endpoint URL handed out at the
start. No API keys, no accounts.

```bash
# 1. install uv (see https://docs.astral.sh/uv/getting-started/installation/)
# 2. from the project folder:
uv sync
cp .env.example .env        # Windows PowerShell: copy .env.example .env
# 3. edit .env and set OLLAMA_HOST to the URL given at the start
```

Run the tests (this is the one command you will live in):

```bash
uv run pytest
```

The agent is run on every ticket first, so the run starts with a **live progress list**
(`[ 7/28] t07 → complaint`, a 🔧 marks a tool call) and ends with a **report**: which
models are agent vs. judge, a per-ticket table (gold → predicted, keywords, tool use,
disputed amount, ✓/✗ with the reason), a per-test-type summary, and your
**production-readiness score**. The whole run takes roughly half a minute.

For just the score (no per-ticket table), set `TRIAGE_REPORT=score`.

Tickets are triaged in parallel (default 4 at a time). A well-provisioned endpoint can
go faster; a throttled one may start dropping tool calls and give you a wrong score, so
raise this only if your endpoint allows real concurrency, and drop to 1 if scores look
unstable:

```bash
TRIAGE_WORKERS=8 uv run pytest       # faster, only if the endpoint can take it
TRIAGE_WORKERS=1 uv run pytest       # safest / most reproducible
```

While iterating, run a single module for faster feedback, e.g.
`uv run pytest tests/test_output.py`.

## Try it as a service desk (web UI)

Before touching tests, it helps to *see* what goes in and out of the agent. The
**Crazy-Busy Itd.** service desk is a one-page web app for exactly that.

```bash
uv run python webapp/server.py
# then open http://localhost:8000 in your browser
# (FastAPI also exposes interactive API docs at http://localhost:8000/docs)
```

Fill in a ticket (subject, description, priority, your own tags) and submit. The page
shows two things side by side:
- **the payload** that is actually sent to the model, so you can see the data structure;
- **the AI triage result**: the category, the keywords, any computed disputed amount,
  and whether the calculator **tool** was used.

The web app uses the same `OLLAMA_HOST` from your `.env`. Stop the server with `Ctrl+C`.
Set a different port with `PORT=9000 uv run python webapp/server.py`.

### Check a ticket programmatically

With the server running, you can hit the same endpoint from Python using `requests`:

```bash
uv run python examples/check_ticket.py
uv run python examples/check_ticket.py "My app crashes when I upload a PDF"
```

It POSTs to `http://localhost:8000/api/classify` and prints the JSON result — handy for
scripting or sanity checks. See `examples/check_ticket.py`.

### Running fully offline (optional)

Install [Ollama](https://ollama.com), then:

```bash
ollama pull llama3.1:8b
# in .env:  OLLAMA_HOST=http://localhost:11434
```

CPU-only inference works but is slower.

### Grade with a stronger judge (optional)

The agent-as-judge module uses an LLM to score keyword quality, and a small model is a
noisy judge. You can keep the agent cheap but grade with a stronger model — set in `.env`:

```bash
MODEL_ID=llama3.1:8b                  # the agent you iterate on
JUDGE_MODEL_ID=gpt-oss:120b-cloud     # only the judge uses this
```

`JUDGE_MODEL_ID` / `JUDGE_OLLAMA_HOST` default to the agent's, so leave them unset to use
one model for everything.

## What you edit

Only **`triage/prompts.py`**, which holds three things:

1. `SYSTEM_PROMPT` — how the agent classifies and when it uses its tool
2. `CALCULATOR_DESC` — what the calculator is and when to call it
3. `JUDGE_RUBRIC` — how the LLM judge grades keyword quality

Do **not** edit the tests, the schema, or the dataset. See `WORKSHOP.md` for the full
task, the recommended order, and the rules of the game.
