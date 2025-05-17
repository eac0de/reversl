from typing import Annotated, Any

from fastapi import APIRouter, Form, HTTPException, Query, Request, Response
from fastapi.datastructures import URL
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

from app.admin_panel.filters.messages import MessagesFilter
from app.admin_panel.filters.users import UsersFilter
from app.config import settings
from app.database import DBSessionDep
from app.dependencies.auth import ADMIN_PANEL_TOKEN_KEY, Auth
from app.dependencies.users import UserDep
from app.models.permission import (
    PERMISSION_CODE_TO_NAME_MAP,
    PERMISSION_GROUPS_MAP,
    PermissionCode,
)
from app.models.user import User
from app.schemas.auth import LoginSchema
from app.schemas.chats import ChatLSchema
from app.services.chats import ChatsService
from app.services.users import UsersService

router = APIRouter(
    tags=["ap_ssr"],
)

static_path = settings.PROJECT_DIR.joinpath("admin_panel", "static")

templates = Jinja2Templates(directory=static_path / "templates")


class Context(dict):  # type: ignore
    def __init__(self, request: Request, *args: Any, **kwargs: Any) -> None:
        if not request:
            raise ValueError("Field 'request' is required")
        kwargs["request"] = request
        super().__init__(*args, **kwargs)


@pass_context
def get_static_url(
    context: dict[str, Any],
    *path_parts: str,
) -> URL:
    request: Request = context["request"]
    return request.url_for("ap_static", path="/".join(path_parts))


templates.env.globals["get_static_url"] = get_static_url


@router.get(
    path="/static/{path:path}",
    name="ap_static",
)
async def get_static(
    path: str,
) -> Response:
    file_path = static_path.joinpath(*path.split("/"))
    if not await file_path.exists() or not await file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )
    return FileResponse(file_path)


@router.get(
    path="/auth/",
    name="ap_auth",
)
async def get_auth_page(
    request: Request,
) -> Response:
    if request.cookies.get(ADMIN_PANEL_TOKEN_KEY):
        return RedirectResponse(url=request.url_for("ap_home"))
    context = {
        "request": request,
    }
    response = templates.TemplateResponse(
        name="auth.j2",
        context=context,
    )
    return response


@router.post(
    path="/auth/login/",
    name="ap_login",
)
async def login(
    request: Request,
    db_session: DBSessionDep,
    schema: Annotated[LoginSchema, Form()],
) -> Response:
    user = await UsersService.auth_user(
        db_session=db_session,
        email=schema.email,
        password=schema.password,
    )
    if not user:
        return RedirectResponse(
            url=request.url_for("ap_auth").include_query_params(error=True),
            status_code=303,
        )
    response = RedirectResponse(
        url=request.url_for("ap_home"),
        status_code=303,
    )
    Auth.set_session_cookie(response, user.uid)
    return response


@router.post(
    path="/auth/logout/",
    name="ap_logout",
)
async def logout(
    request: Request,
) -> Response:
    response = RedirectResponse(
        url=request.url_for("ap_auth"),
        status_code=303,
    )
    Auth.unset_session_cookie(response)
    return response


@router.get(
    path="/",
    name="ap_home",
    dependencies=[
        UserDep(),
    ],
)
async def get_home_page(
    request: Request,
) -> Response:
    context = Context(request=request)
    response = templates.TemplateResponse(
        name="home.j2",
        context=context,
    )
    return response


@router.get(
    path="/users/",
    name="ap_users",
)
async def get_users_page(
    db_session: DBSessionDep,
    request: Request,
    current_user: Annotated[User, UserDep(PermissionCode.R_USER)],
    users_filter: Annotated[UsersFilter, Query(default_factory=UsersFilter)],
) -> Response:
    users_service = UsersService(
        db_session=db_session,
    )
    context = Context(request=request)
    if users_filter.user_uid:
        user = await users_service.get_user_or_none(users_filter.user_uid)
        if not user:
            return RedirectResponse(url=request.url_for("ap_users"))
        context["selected_user"] = users_service.to_user_r_schema(user)
        context["permission_code_name_map"] = PERMISSION_CODE_TO_NAME_MAP
        context["permission_groups"] = PERMISSION_GROUPS_MAP
    users_filter.uid__neq = current_user.uid
    users_list = await users_service.get_users_list(users_filter=users_filter)
    context["users"] = [users_service.to_user_r_schema(user) for user in users_list]
    response = templates.TemplateResponse(
        name="users.j2",
        context=context,
    )
    return response


@router.get(
    path="/chats/",
    name="ap_chats",
    dependencies=[UserDep(PermissionCode.R_CHAT)],
)
async def get_chats_page(
    db_session: DBSessionDep,
    request: Request,
    chat_uid: Annotated[int | None, Query()] = None,
) -> Response:
    chats_service = ChatsService(
        db_session=db_session,
    )
    context: dict[str, Any] = {"request": request}

    if chat_uid:
        chat = await chats_service.get_chat_or_none(chat_uid)
        if not chat:
            return RedirectResponse(url=request.url_for("ap_chats"))
        context["selected_chat"] = chats_service.to_chat_r_schema(chat)
        messages_batch_size = 10
        msgs = await chats_service.get_messages_list(
            chat_uid=chat.uid,
            messages_filter=MessagesFilter(limit=messages_batch_size),
        )
        context["messages"] = [chats_service.to_message_rl_schema(msg) for msg in msgs]
        context["messages_batch_size"] = messages_batch_size

    chats_list = await chats_service.get_chats_list()
    context["chats"] = [ChatLSchema.model_validate(chat) for chat in chats_list]
    response = templates.TemplateResponse(
        name="chats.j2",
        context=context,
    )
    return response
