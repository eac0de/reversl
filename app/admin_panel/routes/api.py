from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse

from app.core.exceptions import ResponseException
from app.database import DBSessionDep
from app.dependencies.users import UserDep
from app.models.permission import PermissionCode
from app.models.user import User
from app.schemas.messages import MessageCSchema
from app.schemas.users import PermissionCodesSchema, UserRSchema, UserUSchema
from app.services.chats_service import ChatsService
from app.services.users_service import UsersService

router = APIRouter(
    tags=["admin_panel_api"],
)


@router.patch(
    path="/users/{user_uid}/",
    name="admin_panel_update_user",
    response_model=UserRSchema,
)
async def update_user(
    user_uid: int,
    user: Annotated[User, UserDep(PermissionCode.U_USER)],
    db_session: DBSessionDep,
    schema: Annotated[UserUSchema, Form()],
) -> UserRSchema:
    users_service = UsersService(
        db_session=db_session,
        user_uid=user.uid,
    )
    u = await users_service.get_user_or_none(user_uid)
    if not u:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    u = await users_service.update_user(
        user=u,
        schema=schema,
    )
    return users_service.to_user_r_schema(u)


@router.patch(
    path="/users/{user_uid}/permissions/",
    name="admin_panel_update_user_permissions",
    response_model=PermissionCodesSchema,
)
async def update_user_permissions(
    user_uid: int,
    user: Annotated[User, UserDep(PermissionCode.U_PERMISSION)],
    db_session: DBSessionDep,
    schema: PermissionCodesSchema,
) -> PermissionCodesSchema:
    users_service = UsersService(
        db_session=db_session,
        user_uid=user.uid,
    )
    u = await users_service.get_user_or_none(user_uid)
    if not u:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    user = await users_service.update_user_permissions(
        user=u,
        schema=schema,
    )
    return PermissionCodesSchema(
        permission_codes={p.code for p in user.permissions},
    )


@router.get(
    path="/message_files/{file_uid}/",
    name="admin_panel_download_message_file",
    response_class=StreamingResponse,
)
async def download_message_file(
    db_session: DBSessionDep,
    user: Annotated[User, UserDep(PermissionCode.R_CHAT)],
    file_uid: int,
) -> StreamingResponse:
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
        content=file_streamer.get_stream(),
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
