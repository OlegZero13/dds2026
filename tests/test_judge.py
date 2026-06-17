"""Module 4 - agent as a judge (hardest).

There is no single ground truth for "good keywords", so we grade them with an LLM
judge (DeepEval's G-Eval) running on the same Ollama endpoint. The judge is only as
good as its rubric: with a vague rubric the scores are noisy and low. You make this
module pass by engineering JUDGE_RUBRIC so the judge reliably recognises relevant,
faithful keywords - including for the long, noisy "needle" ticket.

Fix via JUDGE_RUBRIC in triage/prompts.py.
"""

import concurrent.futures as cf

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from triage.model import get_judge
from triage.prompts import JUDGE_RUBRIC
from tests.thresholds import KEYWORD_JUDGE_MIN

JUDGE_SAMPLE = ["t02", "t04", "t07", "t17", "t28"]


def _score(run) -> float:
    """Build a fresh metric per call so scoring is safe to run in parallel."""
    metric = GEval(
        name="Keyword Quality",
        criteria=JUDGE_RUBRIC,
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        model=get_judge(),
        threshold=KEYWORD_JUDGE_MIN,
    )
    case = LLMTestCase(
        input=run.ticket["text"],
        actual_output=", ".join(run.keywords) or "(none)",
        expected_output=", ".join(run.ticket["reference_keywords"]) or "(none)",
    )
    metric.measure(case)
    return metric.score or 0.0


def test_keyword_quality_average(runs, log):
    log(f"\n⚖️  LLM judge scoring keywords on {len(JUDGE_SAMPLE)} tickets in parallel...")
    scores: dict[str, float] = {}
    with cf.ThreadPoolExecutor(max_workers=len(JUDGE_SAMPLE)) as pool:
        futures = {pool.submit(_score, runs[tid]): tid for tid in JUDGE_SAMPLE}
        for future in cf.as_completed(futures):
            tid = futures[future]
            scores[tid] = future.result()
            log(f"   judged {tid} → {scores[tid]:.2f}")
    avg = sum(scores.values()) / len(scores)
    assert avg >= KEYWORD_JUDGE_MIN, f"avg keyword score {avg:.2f} < {KEYWORD_JUDGE_MIN}; per-ticket: { {k: round(v, 2) for k, v in scores.items()} }"


def test_needle_keywords_are_relevant(runs, log):
    log("\n⚖️  LLM judge scoring the long 'needle' ticket...")
    score = _score(runs["t28"])
    assert score >= KEYWORD_JUDGE_MIN, f"needle keyword score {score:.2f} < {KEYWORD_JUDGE_MIN}"
