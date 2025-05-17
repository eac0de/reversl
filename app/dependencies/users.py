from typing import Any

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.exceptions import ResponseException
from app.database import DBSessionDep
from app.dependencies.auth import Auth, AuthDep
from app.models.permission import PermissionCode
from app.models.user import User
from app.services.users import UsersService


def UserDep(
    *permission_codes: PermissionCode,
) -> Any:
    permission_codes_set = set(permission_codes)

    async def _check_permissions_and_get_user(
        request: Request,
        auth: AuthDep,
        db_session: DBSessionDep,
    ) -> User:
        user = await db_session.scalar(
            select(User)
            .where(User.uid == auth.user_uid)
            .options(
                joinedload(User.permissions),
            )
        )
        if not user:
            response = RedirectResponse(url=request.url_for("ap_auth"))
            Auth.unset_session_cookie(response)
            raise ResponseException(response)
        if permission_codes_set and not permission_codes_set.issubset(
            [p.code for p in user.permissions]
        ):
            raise ResponseException(RedirectResponse(url=request.url_for("ap_home")))
        request.scope["user"] = UsersService.to_user_r_schema(user)
        return user

    return Depends(_check_permissions_and_get_user)
