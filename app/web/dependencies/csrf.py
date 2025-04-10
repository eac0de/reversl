from fastapi import Depends, HTTPException, Request

from app.web.middlewares.csrf import CSRF_TOKEN_KEY


async def verify_csrf_token(request: Request):
    if request.method in ["POST", "PUT", "DELETE"]:
        submitted_token = request.headers.get("X-CSRF-Token") or (
            await request.form()
        ).get("csrf_token")
        if submitted_token != request.cookies.get(CSRF_TOKEN_KEY):
            raise HTTPException(
                status_code=403,
                detail="Invalid CSRF token",
            )


CSRFProtectDep = Depends(verify_csrf_token)
