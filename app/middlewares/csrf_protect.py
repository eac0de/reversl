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
        # TODO исправить, CSRF меняется при любом запросе, даже не относящихся к админ панели
        if (
            not request.scope.get("route")
            or "admin_panel" not in request.scope["route"].name
        ):
            return await call_next(request)
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
