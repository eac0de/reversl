import secrets

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

CSRF_TOKEN_KEY = "reversl-csrf-token"

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Генерируем CSRF-токен, если он ещё не существует
        csrf_token = secrets.token_urlsafe(32)

        # Сохраняем токен в request.state
        request.state.csrf_token = csrf_token

        # Вызываем следующий обработчик
        response = await call_next(request)

        # Устанавливаем CSRF-токен в куки
        response.set_cookie(
            key=CSRF_TOKEN_KEY,
            value=csrf_token,
            httponly=True,  # Защита от доступа из JavaScript
            samesite="strict",  # Защита от CSRF
            secure=False,  # Установите True для HTTPS в продакшене
            max_age=3600,  # Время жизни куки (1 час)
        )

        return response
