from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from backend.core.auth import decode_access_token
from backend.providers.mock.provider import MockProvider
from backend.scheduler.jobs import evaluate_user

router = APIRouter(prefix="/tools", tags=["tools"])
security = HTTPBearer(auto_error=False)


async def get_current_user_key(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing authorization")
    try:
        payload = decode_access_token(creds.credentials)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    user_key = payload.get("user_key")
    if not user_key:
        raise HTTPException(status_code=401, detail="Token missing user_key")
    return str(user_key)


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


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_for_user(
    user_key: str | None = None,
    scenario: str | None = None,
    current_user: str = Depends(get_current_user_key),
) -> EvaluateResponse:
    key = user_key or current_user
    result = await evaluate_user(key, mock=True, scenario=scenario)
    return EvaluateResponse(user=result["user"], suggestions=result["suggestions"])
