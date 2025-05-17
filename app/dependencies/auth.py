from typing import Annotated, Any

import jwt
from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import ResponseException
from app.database import get_db_session
from app.models.chat import Chat

NotAuthenticatedException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


CHAT_TOKEN_KEY = "reversl-chat-token"
CHAT_TOKEN_PATH = (
    f"/{settings.REVERSL_URL_PREFIX}/api/messages/"
    if settings.REVERSL_URL_PREFIX
    else "/api/messages/"
)

ADMIN_PANEL_TOKEN_KEY = "reversl-admin-panel-token"
ADMIN_PANEL_TOKEN_PATH = (
    f"/{settings.REVERSL_URL_PREFIX}/admin/"
    if settings.REVERSL_URL_PREFIX
    else "/admin/"
)


class AuthPayloadSchema(BaseModel):
    user_uid: int = Field(
        title="User ID",
    )


class ChatAuthPayloadSchema(BaseModel):
    chat_uid: int = Field(
        title="Chat ID",
    )


class Auth:
    @classmethod
    def set_session_cookie(
        cls,
        response: Response,
        user_uid: int,
    ) -> None:
        auth_payload = AuthPayloadSchema(user_uid=user_uid)
        response.set_cookie(
            key=ADMIN_PANEL_TOKEN_KEY,
            value=jwt.encode(
                payload=auth_payload.model_dump(mode="json"),
                key=settings.SECRET_KEY,
                algorithm="HS256",
            ),
            httponly=True,
            path=ADMIN_PANEL_TOKEN_PATH,
        )

    @classmethod
    def unset_session_cookie(
        cls,
        response: Response,
    ) -> None:
        response.delete_cookie(
            key=ADMIN_PANEL_TOKEN_KEY,
            path=ADMIN_PANEL_TOKEN_PATH,
            httponly=True,
        )

    @classmethod
    async def get_auth_payload(
        cls,
        request: Request,
        token: Annotated[str | None, Cookie(alias=ADMIN_PANEL_TOKEN_KEY)] = None,
    ) -> AuthPayloadSchema:
        if token is None:
            raise ResponseException(RedirectResponse(url=request.url_for("ap_auth")))
        try:
            payload = cls._get_payload(token)
            return AuthPayloadSchema.model_validate(payload)
        except Exception as e:
            response = RedirectResponse(url=request.url_for("ap_auth"))
            cls.unset_session_cookie(response)
            raise ResponseException(response) from e

    @classmethod
    async def get_chat_auth_payload(
        cls,
        response: Response,
        db_session: Annotated[AsyncSession, Depends(get_db_session)],
        token: Annotated[str | None, Cookie(alias=CHAT_TOKEN_KEY)] = None,
    ) -> Chat:
        try:
            assert token is not None
            payload_data = cls._get_payload(token)
            payload = ChatAuthPayloadSchema.model_validate(payload_data)
            chat = await db_session.get(Chat, payload.chat_uid)
            assert chat is not None
            return chat
        except Exception:
            chat = Chat()
            db_session.add(chat)
            await db_session.commit()
            payload_scheme = ChatAuthPayloadSchema(chat_uid=chat.uid)
            response.set_cookie(
                key=CHAT_TOKEN_KEY,
                value=jwt.encode(
                    payload=payload_scheme.model_dump(),
                    key=settings.SECRET_KEY,
                    algorithm="HS256",
                ),
                httponly=True,
                path=CHAT_TOKEN_PATH,
            )
            return chat

    @staticmethod
    def _get_payload(token: str) -> dict[str, Any]:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])  # type: ignore


AuthDep = Annotated[AuthPayloadSchema, Depends(Auth.get_auth_payload)]
ChatDep = Annotated[Chat, Depends(Auth.get_chat_auth_payload)]
