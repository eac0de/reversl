from pprint import pprint
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.core.exceptions import ResponseException
from app.database import DBSessionDep
from app.dependencies.auth import ADMIN_PANEL_TOKEN_KEY, Auth
from app.dependencies.csrf_protect import CSRFProtectDep
from app.dependencies.users import UserDep
from app.models.permission import PermissionCode
from app.models.user import User
from app.schemas.auth import LoginSchema
from app.schemas.messages import MessageCSchema
from app.services.chats_service import ChatsService
from app.services.users_service import UsersService

router = APIRouter(
    tags=["Admin panel"],
    dependencies=[
        CSRFProtectDep,
    ],
)

templates = Jinja2Templates(
    directory=settings.PROJECT_DIR.joinpath("admin_panel", "static", "templates")
)


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
        UserDep(PermissionCode.R_USER),
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
    selected_user = await users_service.get_user(user_uid=user_uid)
    if not selected_user:
        return RedirectResponse(url=request.url_for("admin_panel_users"))
    context = {
        "request": request,
        "users": await users_service.get_users_list(),
        "selected_user": selected_user,
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
    pprint(m)
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


@router.get(
    path="/message_files/{file_uid}/",
    name="admin_panel_download_message_file",
)
async def download_message_file(
    db_session: DBSessionDep,
    user: Annotated[User, UserDep(PermissionCode.R_CHAT)],
    file_uid: int,
) -> Response:
    chats_service = ChatsService(
        db_session=db_session,
        user_uid=user.uid,
    )
    file_streamer = await chats_service.download_message_file(file_uid)
    if not file_streamer:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )
    return StreamingResponse(
        content=file_streamer.get_bytes_stream(),
        media_type=file_streamer.media_type,
        headers={"Content-Disposition": file_streamer.content_disposition},
    )


@router.post(
    path="/chats/{chat_uid}/messages/",
    name="admin_panel_send_message",
)
async def send_message(
    db_session: DBSessionDep,
    request: Request,
    chat_uid: int,
    user: Annotated[User, UserDep(PermissionCode.R_CHAT)],
    schema: Annotated[MessageCSchema, Form(media_type="multipart/form-data")],
) -> None:
    chats_service = ChatsService(
        db_session=db_session,
        user_uid=user.uid,
    )
    chat = await chats_service.get_chat(chat_uid)
    if not chat:
        raise ResponseException(
            RedirectResponse(
                url=request.url_for("admin_panel_chats"),
                status_code=303,
            )
        )
    await chats_service.create_message(
        chat_uid=chat.uid,
        user_uid=user.uid,
        schema=schema,
    )
