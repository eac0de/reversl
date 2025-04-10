from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.core.exceptions import ResponseException
from app.database import DBSessionDep
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
    user_uid: UUID = Field(
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
        user_uid: UUID,
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
            raise ResponseException(
                RedirectResponse(url=request.url_for("admin_panel_auth"))
            )
        try:
            payload = cls._get_payload(token)
            return AuthPayloadSchema.model_validate(payload)
        except Exception as e:
            raise ResponseException(
                RedirectResponse(url=request.url_for("admin_panel_auth"))
            ) from e

    @classmethod
    async def get_chat_auth_payload(
        cls,
        response: Response,
        db_session: DBSessionDep,
        token: Annotated[str | None, Cookie(alias=CHAT_TOKEN_KEY)] = None,
    ) -> ChatAuthPayloadSchema:
        if token is None:
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
            return payload_scheme
        try:
            payload = cls._get_payload(token)
            return ChatAuthPayloadSchema.model_validate(payload)
        except Exception as e:
            raise NotAuthenticatedException from e

    @staticmethod
    def _get_payload(token: str) -> dict[str, Any]:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


AuthDep = Annotated[AuthPayloadSchema, Depends(Auth.get_auth_payload)]
ChatAuthDep = Annotated[ChatAuthPayloadSchema, Depends(Auth.get_chat_auth_payload)]
