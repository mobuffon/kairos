from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from backend.scheduler.jobs import evaluate_user

SCENARIOS_PATH = Path(__file__).resolve().parents[2] / "tests" / "selftest" / "scenarios.yaml"


@dataclass
class ScenarioResult:
    scenario_id: str
    passed: bool
    message: str
    details: dict[str, Any]


def load_scenarios(path: Path | None = None) -> list[dict[str, Any]]:
    p = path or SCENARIOS_PATH
    with p.open() as f:
        return yaml.safe_load(f) or []


async def run_scenario(spec: dict[str, Any]) -> ScenarioResult:
    result = await evaluate_user(
        spec["user"],
        mock=True,
        scenario=spec["scenario"],
    )
    suggestions = result.get("suggestions", [])
    hobby = spec["hobby"]
    matching = [s for s in suggestions if s["hobby_type"] == hobby]
    expect = spec.get("expect_suggest", True)

    if expect:
        if not matching:
            return ScenarioResult(
                spec["id"],
                False,
                f"Expected {hobby} suggestion but got none",
                {"suggestions": suggestions},
            )
        top = matching[0]
        min_score = spec.get("min_score", 0.5)
        if top["score"] < min_score:
            return ScenarioResult(
                spec["id"],
                False,
                f"Score {top['score']} below min {min_score}",
                {"top": top},
            )
        return ScenarioResult(spec["id"], True, "Suggestion matched expectations", {"top": top})

    if matching:
        return ScenarioResult(
            spec["id"],
            False,
            f"Expected no {hobby} suggestion but got score {matching[0]['score']}",
            {"top": matching[0]},
        )
    return ScenarioResult(spec["id"], True, "Correctly suppressed suggestion", {})


async def run_all_scenarios(path: Path | None = None) -> list[ScenarioResult]:
    specs = load_scenarios(path)
    results: list[ScenarioResult] = []
    for spec in specs:
        results.append(await run_scenario(spec))
    return results
