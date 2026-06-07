from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.core.auth import create_access_token, dev_user_ids
from backend.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


class DevLoginRequest(BaseModel):
    user: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


@router.get("/google/url")
async def google_oauth_url() -> dict[str, str]:
    """Return Google OAuth authorization URL (stub when credentials missing)."""
    settings = get_settings()
    if settings.use_mock_calendar:
        return {
            "url": f"{settings.frontend_url}/settings?calendar=mock",
            "mock": "true",
            "message": "Google OAuth not configured — using mock calendar provider",
        }
    scopes = "https://www.googleapis.com/auth/calendar"
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        "&response_type=code"
        f"&scope={scopes}"
        "&access_type=offline"
        "&prompt=consent"
    )
    return {"url": url, "mock": "false"}


@router.post("/dev-login", response_model=TokenResponse)
async def dev_login(body: DevLoginRequest) -> TokenResponse:
    """Issue JWT for mock users in local development only."""
    ids = dev_user_ids()
    if body.user not in ids:
        raise HTTPException(status_code=404, detail=f"Unknown dev user: {body.user}")
    user_id = ids[body.user]
    token = create_access_token(str(user_id), extra={"user_key": body.user})
    return TokenResponse(access_token=token, user_id=str(user_id))
