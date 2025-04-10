from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse

from app.database import DBSessionDep
from app.schemas.messages import MessageCSchema, MessageRLSchema
from app.services.api_service import APIService
from app.web.dependencies.auth import ChatAuthDep

router = APIRouter()


@router.post(
    path="/messages/",
    response_model=MessageRLSchema,
)
async def create_message(
    db_session: DBSessionDep,
    chat_auth: ChatAuthDep,
    schema: MessageCSchema = Form(media_type="multipart/form-data"),
) -> MessageRLSchema:
    api_service = APIService(
        db_session=db_session,
        chat_id=chat_auth.chat_uid,
    )
    return await api_service.create_message(schema)


@router.get(
    path="/messages/",
    response_model=list[MessageRLSchema],
)
async def get_messages_list(
    db_session: DBSessionDep,
    chat_auth: ChatAuthDep,
) -> list[MessageRLSchema]:
    api_service = APIService(
        db_session=db_session,
        chat_id=chat_auth.chat_uid,
    )
    return await api_service.get_messages_list()


@router.get(
    path="/messages/files/{file_uid}/",
    response_class=StreamingResponse,
)
async def download_message_file(
    db_session: DBSessionDep,
    chat_auth: ChatAuthDep,
    file_uid: int,
) -> StreamingResponse:
    api_service = APIService(
        db_session=db_session,
        chat_id=chat_auth.chat_uid,
    )
    file_streamer = await api_service.download_message_file(
        file_uid=file_uid,
    )
    return StreamingResponse(
        content=file_streamer.get_bytes_stream(),
        media_type=file_streamer.media_type,
        headers={"Content-Disposition": file_streamer.content_disposition},
    )
