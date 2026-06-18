# Staged solutions for llama3.1:8b (organizer-only)

Step-by-step prompt versions that show attendees how to improve the agent **on the weak
local model**. Run any with the helper (swaps it in, runs the suite, restores your copy):

```bash
uv run python scripts/check_solution.py solution/prompts_2_tools.py
```

## The headline slide: the same stages on three models

Same data, same staged prompts, deterministic run (`TRIAGE_WORKERS=1`, temperature 0).
Score = % of the **12 tests** passing (includes the off-topic trap below).

| Stage (what the prompt adds) | llama3.2:3b | llama3.1:8b | gpt-oss:120b-cloud | 8B agent + 120B judge |
|------------------------------|:-----------:|:-----------:|:------------------:|:---------------------:|
| 0 — weak start              | 50% | 50% | 58% | 58% |
| 1 — output formulation      | 58% | 58% | 58% | 58% |
| 2 — tool usage              | 58% | **42%** | **92%** | 50% |
| 3 — guardrails              | 83% | 58% | 92% | 75% |
| 4 — agent-as-judge          | **83%** | 58% | **100%** | 83% |

Read it as a climb, not a clean staircase. The off-topic trap (12th test) gives every config
a real **Stage-1 (output) gain** (50→58). After that:
- **gpt-oss:120b-cloud** is the cleanest: 58→58→92→92→**100**.
- **llama3.2:3b** climbs steadily to 83%: 50→58→58→83→83.
- **llama3.1:8b alone** is the noisiest — it even *dips* at Stage 2 (58→42) and ends at 58%,
  because the 8B agent is non-deterministic on borderline tickets (keywords, the long needle)
  and is a noisy judge.
- **8B agent + 120B judge** fixes the judge half (Stage 4 lifts to 83%), but the agent's own
  noise still dents the middle (Stage 2 dip).

What attendees should take away:

- **The output stage now counts for everyone** — the off-topic category gives a robust
  red→green at Stage 1 (50→58 on the small models).
- **Small models plateau at ~83%** — they never cleanly clear the judge module. An
  LLM-as-judge is only as good as the judge model, and llama3.1:8b/3.2:3b are too noisy.
- **The strong model reaches 100%** and shows the *cleanest climb* (58→58→92→92→100): it is
  more **steerable**, so each prompt stage genuinely moves its behaviour.
- **8B alone is too noisy for a clean staircase** — its run-to-run variance produces a dip at
  Stage 2 (a borderline-ticket flap, not a real regression). A stronger judge fixes the judge
  half; the agent's own noise is what still wobbles the middle.

So the honest answer to "why doesn't the score rise at every stage on 8B?" is: it does on a
model good enough to listen. Pick the model to match the lesson you want to show.

## Best of both: cheap agent, strong judge

You can keep the **agent** on the cheap local model and run only the **judge** on the strong
one. In `.env`:

```bash
MODEL_ID=llama3.1:8b          # the agent attendees iterate on (cheap, local)
JUDGE_MODEL_ID=gpt-oss:120b-cloud   # grades keyword quality reliably
```

Result (12 tests): **58 → 58 → 50 → 75 → 83**. The win is Stage 4: with a *reliable* judge the
agent-as-judge module finally **counts** — it goes red→green when you engineer the rubric
(weak rubric scores avg ~0.58, the engineered rubric ~0.76). And crucially, the strong judge
still **respects the rubric**, so `JUDGE_RUBRIC` remains a real tunable surface — it is just no
longer drowned in 8B judge noise. The middle still dips (Stage 2 = 50%) because the 8B *agent*
itself is non-deterministic on a couple of borderline tickets; the strong judge fixes the
evaluation, not the agent. It tops out at 83%, not 100%, because the 8B agent — not the judge —
is the remaining limit.

This is the recommended setup if you want every test type to matter on a cheap agent: it
separates "is the agent good?" (8B, the thing attendees improve) from "is our evaluation
trustworthy?" (strong judge) — which is exactly the right lesson about LLM-as-judge.

## Hidden trap: off-topic detection (12th test)

The dataset has 3 junk tickets — a weather question, gibberish, a recipe request (t25–t27,
tag `off_topic`). There is a **fifth category `off_topic`** in the schema, and a test
(`test_off_topic_tickets_are_detected`) that requires those tickets to be routed there. But
the **starter prompt never mentions it** — it is a deliberate trap. The weak agent forces
the junk into `feature_request`/`complaint` (the report shows them as ❌), so the output
module sits at 3/4. An attendee who notices adds the category to `SYSTEM_PROMPT`
(`off_topic: spam, gibberish, unrelated to support`) and it flips to 4/4.

This is the one **robust gain at Stage 1 (output)** on a small model: the weak prompt
*definitely* doesn't know the category and the solution *definitely* does — nothing
borderline. (The rest of the 8B trajectory still wobbles ±1–2 tests between runs because the
8B agent is non-deterministic on keywords / the long needle — e.g. one refresh gave
50→58→42→58→58. The off-topic flip itself is reliable; the surrounding noise is not.)

All `solution/prompts_*.py` already include the `off_topic` category, so the reference
solution detects it.

## The 8B trajectory in detail (verified, temperature 0)

| Stage | File | Focus | Score | What changes |
|------:|------|-------|:-----:|--------------|
| 0 | `prompts_0_start.py` | the weak start | **~55%** | smoke + **output already pass** |
| 1 | `prompts_1_output.py` | output formulation | ~55% | output stays green (it was already solid) |
| 2 | `prompts_2_tools.py` | tool usage | **~64%** | **tools go green** (calculator + correct amount) |
| 3 | `prompts_3_guardrails.py` | guardrails | **~82%** | **guardrails go green** (injections resisted) |
| 4 | `prompts_4_judge.py` | agent-as-judge | ~82% | judge score rises (~0.42→~0.64) but stays under 0.70 |

## The key lesson to teach (and why the score does not rise at every step)

We tried hard to make every stage raise the score by editing only the data. It cannot be
done on a small local model, and **that is itself the lesson**:

- **Output is the easy part.** Classifying a clear ticket into 4 obvious buckets is trivial
  for any modern LLM, even with a one-line prompt — and the Pydantic enum guarantees a
  valid label for free. So Stage 1 has nothing to "fix"; it confirms the contract. (We even
  tried removing the enum so the weak model would emit messy labels like `Billing/Refund` —
  but then it *cannot reliably produce clean labels even when told to*, which breaks the
  whole pipeline. And boundary-case tickets flip between runs because Ollama batches
  parallel requests. Both dead ends are documented in the repo history.)
- **Tools and guardrails are the real work.** Small models genuinely fail at money math and
  at resisting prompt injection, and a good prompt genuinely fixes both. This is where the
  score visibly climbs (Stages 2 and 3) — the honest payoff of prompt engineering.
- **The judge is the ceiling.** An LLM-as-judge is only as reliable as the judge model.
  llama3.1:8b as a G-Eval judge is noisy: the same good keywords score anywhere from 0.2 to
  0.8, and the average swings ~0.36–0.64 between runs. A better rubric helps measurably, but
  you cannot prompt your way past a weak, noisy judge.

So frame it as: **every test *type* matters** — output proves the contract is solid, tools
and guardrails are where prompts pay off, and the judge shows the limits of LLM evaluation —
even though the *number* only jumps at Stages 2 and 3.

### Want the number to climb at every stage?

That requires a model that is weak enough to fail output yet stable enough to respond
cleanly to prompts — a sweet spot that does not exist among these small models (a 3B model
still aces output; anything weaker is too chaotic to grade reliably). The clean,
fully-reproducible 0→100% climb only appears on a strong model:

```bash
MODEL_ID=gpt-oss:120b-cloud uv run python scripts/check_solution.py solution/prompts.py
```

`solution/prompts.py` reaches **11/11 (100%)** there. The staged files above are the honest
8B story; use them to teach the techniques and the limits side by side.
```
