from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.core.auth import decode_access_token

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
