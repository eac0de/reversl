from typing import Annotated, Any

from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.datastructures import URL
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

from app.config import settings
from app.database import DBSessionDep
from app.dependencies.auth import ADMIN_PANEL_TOKEN_KEY, Auth
from app.dependencies.users import UserDep
from app.models.permission import PERMISSION_CODE_TO_NAME_MAP, PermissionCode
from app.models.user import User
from app.schemas.auth import LoginSchema
from app.services.chats_service import ChatsService
from app.services.users_service import UsersService

router = APIRouter(
    tags=["admin_panel_ssr"],
)

static_path = settings.PROJECT_DIR.joinpath("admin_panel", "static")

templates = Jinja2Templates(directory=static_path / "templates")


@pass_context
def get_static_url(
    context: dict[str, Any],
    *path_parts: str,
) -> URL:
    request: Request = context["request"]
    return request.url_for("admin_panel_static", path="/".join(path_parts))


templates.env.globals["get_static_url"] = get_static_url


@router.get(
    path="/static/{path:path}",
    name="admin_panel_static",
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
    name="admin_panel_auth",
)
async def get_auth_page(
    request: Request,
) -> Response:
    if request.cookies.get(ADMIN_PANEL_TOKEN_KEY):
        return RedirectResponse(url=request.url_for("admin_panel_home"))
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
    name="admin_panel_login",
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
            url=request.url_for("admin_panel_auth").include_query_params(error=True),
            status_code=303,
        )
    response = RedirectResponse(
        url=request.url_for("admin_panel_home"),
        status_code=303,
    )
    Auth.set_session_cookie(response, user.uid)
    return response


@router.post(
    path="/auth/logout/",
    name="admin_panel_logout",
)
async def logout(
    request: Request,
) -> Response:
    response = RedirectResponse(
        url=request.url_for("admin_panel_auth"),
        status_code=303,
    )
    Auth.unset_session_cookie(response)
    return response


@router.get(
    path="/",
    name="admin_panel_home",
    dependencies=[
        UserDep(),
    ],
)
async def get_home_page(
    request: Request,
) -> Response:
    context = {
        "request": request,
    }
    response = templates.TemplateResponse(
        name="home.j2",
        context=context,
    )
    return response


@router.get(
    path="/users/",
    name="admin_panel_users",
)
async def get_users_page(
    db_session: DBSessionDep,
    user: Annotated[User, UserDep(PermissionCode.R_USER)],
    request: Request,
) -> Response:
    users_service = UsersService(
        db_session=db_session,
        user_uid=user.uid,
    )
    context = {
        "request": request,
        "users": await users_service.get_users_list(),
    }
    response = templates.TemplateResponse(
        name="users.j2",
        context=context,
    )
    return response


@router.get(
    path="/users/{user_uid}/",
    name="admin_panel_user",
)
async def get_user_page(
    user_uid: int,
    user: Annotated[User, UserDep(PermissionCode.R_USER)],
    db_session: DBSessionDep,
    request: Request,
) -> Response:
    users_service = UsersService(
        db_session=db_session,
        user_uid=user.uid,
    )
    selected_user = await users_service.get_user_or_none(
        user_uid=user_uid,
        join_permissions=True,
    )
    if not selected_user:
        return RedirectResponse(url=request.url_for("admin_panel_users"))
    context = {
        "request": request,
        "users": await users_service.get_users_list(),
        "selected_user": users_service.to_user_r_schema(selected_user),
        "permission_code_to_name_map": PERMISSION_CODE_TO_NAME_MAP,
    }
    response = templates.TemplateResponse(
        name="users.j2",
        context=context,
    )
    return response


@router.get(
    path="/chats/",
    name="admin_panel_chats",
)
async def get_chats_page(
    db_session: DBSessionDep,
    user: Annotated[User, UserDep(PermissionCode.R_CHAT)],
    request: Request,
) -> Response:
    chats_service = ChatsService(
        db_session=db_session,
        user_uid=user.uid,
    )
    context = {
        "request": request,
        "chats": await chats_service.get_chats_list(),
    }
    response = templates.TemplateResponse(
        name="chats.j2",
        context=context,
    )
    return response


@router.get(
    path="/chats/{chat_uid}/",
    name="admin_panel_chat",
    dependencies=[
        UserDep(PermissionCode.R_CHAT),
    ],
)
async def get_chat_page(
    db_session: DBSessionDep,
    user: Annotated[User, UserDep(PermissionCode.R_CHAT)],
    request: Request,
    chat_uid: int,
) -> Response:
    chats_service = ChatsService(
        db_session=db_session,
        user_uid=user.uid,
    )
    chat = await chats_service.get_chat(chat_uid)
    if not chat:
        return RedirectResponse(url=request.url_for("admin_panel_chats"))
    m = await chats_service.get_chat_messages(chat.uid)
    context = {
        "request": request,
        "chats": await chats_service.get_chats_list(),
        "selected_chat": chat,
        "messages": m,
    }
    response = templates.TemplateResponse(
        name="chats.j2",
        context=context,
    )
    return response
