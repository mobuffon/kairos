from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.api.deps import get_current_user_key
from backend.providers.mock.provider import MockProvider
from backend.scheduler.jobs import evaluate_user
from backend.selftest.scenario_runner import run_all_scenarios

router = APIRouter(prefix="/tools", tags=["tools"])


class EvaluateResponse(BaseModel):
    user: str
    suggestions: list[dict[str, Any]]


@router.get("/connections")
async def list_connections() -> dict[str, list[str]]:
    provider = MockProvider()
    return {
        "users": provider.list_users(),
        "scenarios": provider.list_scenarios(),
    }


@router.get("/selftest")
async def run_selftest() -> dict[str, Any]:
    results = await run_all_scenarios()
    passed = sum(1 for r in results if r.passed)
    return {
        "passed": passed,
        "total": len(results),
        "all_passed": passed == len(results),
        "results": [
            {"id": r.scenario_id, "passed": r.passed, "message": r.message} for r in results
        ],
    }


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_for_user(
    user_key: str | None = None,
    scenario: str | None = None,
    current_user: str = Depends(get_current_user_key),
) -> EvaluateResponse:
    key = user_key or current_user
    result = await evaluate_user(key, mock=True, scenario=scenario)
    return EvaluateResponse(user=result["user"], suggestions=result["suggestions"])
