from uuid import UUID

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import DBSessionDep
from app.models.permission import PermissionCode
from app.schemas.auth import LoginSchema
from app.services.chats_service import ChatsService
from app.services.users_service import UsersService
from app.web.dependencies.auth import ADMIN_PANEL_TOKEN_KEY, Auth
from app.web.dependencies.csrf import CSRFProtectDep
from app.web.dependencies.users import UserDep

router = APIRouter(
    tags=["Admin panel"],
    dependencies=[
        CSRFProtectDep,
    ],
)

templates = Jinja2Templates(
    directory=settings.PROJECT_DIR.joinpath("web", "admin_panel", "static", "templates")
)


@router.get(
    path="/auth/",
    name="admin_panel_auth",
)
async def get_auth_page(
    request: Request,
):
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
    schema: LoginSchema = Form(),
):
    users_service = UsersService(db_session=db_session)
    user = await users_service.auth_user(
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
):
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
        UserDep(PermissionCode.R_USER),
    ],
)
async def get_home_page(
    request: Request,
):
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
    dependencies=[
        UserDep(PermissionCode.R_USER),
    ],
)
async def get_users_page(
    db_session: DBSessionDep,
    request: Request,
):
    users_service = UsersService(db_session=db_session)
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
    dependencies=[
        UserDep(PermissionCode.R_USER),
    ],
)
async def get_user_page(
    user_uid: UUID,
    db_session: DBSessionDep,
    request: Request,
):
    users_service = UsersService(db_session=db_session)
    user = await users_service.get_user(user_uid=user_uid)
    if not user:
        return RedirectResponse(url=request.url_for("admin_panel_users"))
    context = {
        "request": request,
        "users": await users_service.get_users_list(),
        "selected_user": await users_service.get_user(user_uid=user_uid),
    }
    response = templates.TemplateResponse(
        name="users.j2",
        context=context,
    )
    return response


@router.get(
    path="/chats/",
    name="admin_panel_chats",
    dependencies=[
        UserDep(PermissionCode.R_CHAT),
    ],
)
async def get_chats_page(
    db_session: DBSessionDep,
    request: Request,
):
    chats_service = ChatsService(db_session=db_session)
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
    request: Request,
    chat_uid: int,
):
    chats_service = ChatsService(db_session=db_session)
    chat = await chats_service.get_chat(chat_uid)
    if not chat:
        return RedirectResponse(url=request.url_for("admin_panel_chats"))
    context = {
        "request": request,
        "chats": await chats_service.get_chats_list(),
        "selected_chat": chat,
        "messages": await chats_service.get_chat_messages(chat.uid),
    }
    response = templates.TemplateResponse(
        name="chats.j2",
        context=context,
    )
    return response


@router.get(
    path="/message_files/{file_uid}/",
    name="admin_panel_download_message_image",
    dependencies=[
        UserDep(PermissionCode.R_CHAT),
    ],
)
async def download_message_image(
    db_session: DBSessionDep,
    request: Request,
    file_uid: int,
):
    chats_service = ChatsService(db_session=db_session)
    chat = await chats_service.get_chat(file_uid)
    if not chat:
        return HTTPException(status_code=404, detail="File not found")
    context = {
        "request": request,
        "chats": await chats_service.get_chats_list(),
        "selected_chat": chat,
        "messages": await chats_service.get_chat_messages(chat.uid),
    }
    response = templates.TemplateResponse(
        name="chats.j2",
        context=context,
    )
    return response
