from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse, StreamingResponse

from app.admin_panel.filters.messages import MessagesFilter
from app.core.exceptions import ResponseException
from app.database import DBSessionDep, with_commit
from app.dependencies.users import UserDep
from app.models.permission import PermissionCode
from app.models.user import User
from app.schemas.chats import ChatRSchema, ChatUSchema
from app.schemas.messages import MessageCSchema, MessageRLSchema
from app.schemas.users import PermissionCodesSchema, UserRSchema, UserUSchema
from app.services.chats import ChatsService
from app.services.users import UsersService

router = APIRouter(
    tags=["ap_api"],
)


@router.patch(
    path="/users/{user_uid}/",
    name="ap_update_user",
    response_model=UserRSchema,
    dependencies=[UserDep(PermissionCode.U_USER)],
)
async def update_user(
    user_uid: int,
    db_session: DBSessionDep,
    schema: Annotated[UserUSchema, Form()],
) -> UserRSchema:
    users_service = UsersService(
        db_session=db_session,
    )
    user = await users_service.get_user_or_none(user_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    async with with_commit(db_session):
        user = await users_service.update_user(
            user=user,
            schema=schema,
        )
    return users_service.to_user_r_schema(user)


@router.patch(
    path="/users/{user_uid}/permissions/",
    name="ap_update_user_permissions",
    response_model=PermissionCodesSchema,
)
async def update_user_permissions(
    current_user: Annotated[User, UserDep(PermissionCode.U_PERMISSION)],
    user_uid: int,
    db_session: DBSessionDep,
    schema: PermissionCodesSchema,
) -> PermissionCodesSchema:
    users_service = UsersService(
        db_session=db_session,
    )
    user = await users_service.get_user_or_none(user_uid)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    async with with_commit(db_session):
        permissions = await users_service.update_user_permissions(
            current_user_uid=current_user.uid,
            user=user,
            schema=schema,
        )
    return PermissionCodesSchema(
        permission_codes={p.code for p in permissions},
    )


@router.get(
    path="/chats/{chat_uid}/files/{file_uid}/",
    name="ap_download_message_file",
    response_class=StreamingResponse,
    dependencies=[UserDep(PermissionCode.R_CHAT)],
)
async def download_message_file(
    db_session: DBSessionDep,
    chat_uid: int,
    file_uid: int,
) -> StreamingResponse:
    chats_service = ChatsService(
        db_session=db_session,
    )
    file_streamer = await chats_service.download_message_file(
        chat_uid=chat_uid,
        file_uid=file_uid,
    )
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
    name="ap_send_message",
)
async def create_message(
    db_session: DBSessionDep,
    request: Request,
    chat_uid: int,
    current_user: Annotated[User, UserDep(PermissionCode.R_CHAT)],
    schema: Annotated[MessageCSchema, Form(media_type="multipart/form-data")],
) -> MessageRLSchema:
    chats_service = ChatsService(
        db_session=db_session,
    )
    chat = await chats_service.get_chat_or_none(chat_uid=chat_uid)
    if not chat:
        raise ResponseException(
            RedirectResponse(
                url=request.url_for("ap_chats"),
                status_code=303,
            )
        )
    async with with_commit(db_session):
        msg = await chats_service.create_message(
            chat_uid=chat.uid,
            schema=schema,
            current_user=current_user,
        )
    return chats_service.to_message_rl_schema(msg)


@router.get(
    path="/chats/{chat_uid}/messages/",
    response_model=list[MessageRLSchema],
    name="ap_get_messages_list",
    dependencies=[UserDep(PermissionCode.R_MESSAGE)],
)
async def get_messages_list(
    db_session: DBSessionDep,
    chat_uid: int,
    messages_filter: Annotated[MessagesFilter, Query(default_factory=MessagesFilter)],
) -> list[MessageRLSchema]:
    service = ChatsService(
        db_session=db_session,
    )
    messages_list = await service.get_messages_list(
        chat_uid=chat_uid,
        messages_filter=messages_filter,
    )
    return [service.to_message_rl_schema(message) for message in messages_list]


@router.patch(
    path="/chats/{chat_uid}/",
    response_model=ChatRSchema,
    name="ap_update_chat",
)
async def update_chat(
    db_session: DBSessionDep,
    chat_uid: int,
    schema: Annotated[ChatUSchema, Form(media_type="multipart/form-data")],
) -> ChatRSchema:
    service = ChatsService(
        db_session=db_session,
    )
    chat = await service.get_chat_or_none(chat_uid=chat_uid)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
    async with with_commit(db_session):
        chat = await service.update_chat(
            chat=chat,
            schema=schema,
        )
    return service.to_chat_r_schema(chat)


# @router.websocket(
#     path="/ws/",
#     name="ap_ws",
#     dependencies=[UserDep(PermissionCode.U_PERMISSION)],
# )
# async def websocket_endpoint(
#     websocket: WebSocket,
#     current_user: Annotated[User, UserDep(PermissionCode.U_PERMISSION)],
#     db_session: DBSessionDep,
# ):
#     await ws_handler(
#         websocket=websocket,
#         db_session=db_session,
#         current_user=current_user,
# )
