import pytest

from backend.selftest.llm_evaluator import evaluate_message_quality
from backend.selftest.scenario_runner import run_all_scenarios


@pytest.mark.asyncio
async def test_all_yaml_scenarios_pass():
    results = await run_all_scenarios()
    failures = [r for r in results if not r.passed]
    assert not failures, failures


@pytest.mark.asyncio
async def test_llm_evaluator_mock():
    result = await evaluate_message_quality(
        "Surf looks great tomorrow at 7:30 with 1.6m swell.",
        {"hobby_type": "surf"},
        mock=True,
    )
    assert result.passed
    assert result.score >= 0.6
