from fastapi import Depends, HTTPException, Request

from app.config import settings


async def verify_csrf_token(request: Request) -> None:
    if request.method != "GET":
        submitted_token = request.headers.get("X-CSRF-Token") or (
            await request.form()
        ).get("csrf_token")
        if submitted_token != request.cookies.get(settings.REVERSL_CSRF_TOKEN_KEY):
            raise HTTPException(
                status_code=403,
                detail="Invalid CSRF token",
            )


CSRFProtectDep = Depends(verify_csrf_token)
