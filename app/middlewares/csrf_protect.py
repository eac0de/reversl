import secrets

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.config import settings


class CSRFProtectMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if csrf_token := request.cookies.get(settings.REVERSL_CSRF_TOKEN_KEY):
            pass
        else:
            csrf_token = secrets.token_urlsafe(32)
        request.state.csrf_token = csrf_token
        response = await call_next(request)
        response.set_cookie(
            key=settings.REVERSL_CSRF_TOKEN_KEY,
            value=csrf_token,
            httponly=True,
            samesite="strict",
            secure=False,
            max_age=3600,
        )

        return response
