from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.auth import create_access_token, dev_user_ids

router = APIRouter(prefix="/auth", tags=["auth"])


class DevLoginRequest(BaseModel):
    user: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


@router.post("/dev-login", response_model=TokenResponse)
async def dev_login(body: DevLoginRequest) -> TokenResponse:
    """Issue JWT for mock users in local development only."""
    ids = dev_user_ids()
    if body.user not in ids:
        raise HTTPException(status_code=404, detail=f"Unknown dev user: {body.user}")
    user_id = ids[body.user]
    token = create_access_token(str(user_id), extra={"user_key": body.user})
    return TokenResponse(access_token=token, user_id=str(user_id))
