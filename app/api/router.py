import json
from typing import Annotated

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import StreamingResponse

from app.admin_panel.filters.messages import MessagesFilter
from app.core.constants import AP_REDIS_CHANNEL, CHAT_REDIS_CHANNEL_PATTERN
from app.core.database import DBSessionDep, with_commit
from app.core.rediss import get_redis
from app.dependencies.auth import ChatDep
from app.schemas.chats import ChatRSchema, ChatUSchema
from app.schemas.messages import MessageCSchema, MessageRLSchema
from app.services.chats import ChatsService

router = APIRouter()


@router.post(
    path="/messages/",
)
async def create_message(
    db_session: DBSessionDep,
    chat: ChatDep,
    schema: Annotated[MessageCSchema, Form(media_type="multipart/form-data")],
) -> None:
    service = ChatsService(
        db_session=db_session,
    )
    async with with_commit(db_session):
        msg = await service.create_message(
            chat_uid=chat.uid,
            schema=schema,
        )
    redis_msg = json.dumps(
        {
            "type": "message",
            "chat_uid": chat.uid,
            "message_uid": msg.uid,
        }
    )
    redis = get_redis()
    await redis.publish(AP_REDIS_CHANNEL, redis_msg)
    await redis.publish(CHAT_REDIS_CHANNEL_PATTERN.format(chat.uid), redis_msg)


@router.patch(
    path="/chat/",
    response_model=MessageRLSchema,
)
async def update_chat(
    db_session: DBSessionDep,
    chat: ChatDep,
    schema: Annotated[ChatUSchema, Form(media_type="multipart/form-data")],
) -> ChatRSchema:
    service = ChatsService(
        db_session=db_session,
    )
    async with with_commit(db_session):
        chat = await service.update_chat(
            chat=chat,
            schema=schema,
        )
    return service.to_chat_r_schema(chat)


@router.get(
    path="/messages/",
    response_model=list[MessageRLSchema],
)
async def get_messages_list(
    db_session: DBSessionDep,
    chat: ChatDep,
    messages_filter: Annotated[MessagesFilter, Query(default_factory=MessagesFilter)],
) -> list[MessageRLSchema]:
    service = ChatsService(
        db_session=db_session,
    )
    messages_list = await service.get_messages_list(
        chat_uid=chat.uid,
        messages_filter=messages_filter,
    )
    return [service.to_message_rl_schema(message) for message in messages_list]


@router.get(
    path="/messages/{message_uid}/",
    response_model=MessageRLSchema,
)
async def get_message(
    db_session: DBSessionDep,
    chat: ChatDep,
    message_uid: int,
) -> MessageRLSchema:
    service = ChatsService(
        db_session=db_session,
    )
    message = await service.get_message_or_none(
        chat_uid=chat.uid,
        message_uid=message_uid,
    )
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    return service.to_message_rl_schema(message)


@router.get(
    path="/files/{file_uid}/",
    response_class=StreamingResponse,
)
async def download_message_file(
    db_session: DBSessionDep,
    chat: ChatDep,
    file_uid: int,
) -> StreamingResponse:
    service = ChatsService(
        db_session=db_session,
    )
    file_streamer = await service.download_message_file(
        chat_uid=chat.uid,
        file_uid=file_uid,
    )
    return StreamingResponse(
        content=file_streamer.get_stream(),
        media_type=file_streamer.media_type,
        headers={"Content-Disposition": file_streamer.content_disposition},
    )


@router.get(
    path="/",
    response_model=ChatRSchema,
)
async def get_chat(
    db_session: DBSessionDep,
    chat: ChatDep,
) -> ChatRSchema:
    service = ChatsService(
        db_session=db_session,
    )
    return service.to_chat_r_schema(chat)


@router.websocket(
    path="/ws/",
)
async def websocket_endpoint(
    websocket: WebSocket,
    chat: ChatDep,
) -> None:
    await websocket.accept()
    redis = get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(CHAT_REDIS_CHANNEL_PATTERN.format(chat.uid))
    try:
        async for msg in pubsub.listen():
            await websocket.send_text(msg)
    except WebSocketDisconnect:
        await pubsub.close()
