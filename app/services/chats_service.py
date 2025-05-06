from uuid import uuid4

import magic
from anyio import Path
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import settings
from app.models.chat import Chat
from app.models.message import Message
from app.models.message_file import MessageFile
from app.schemas.chats import ChatLSchema, ChatRSchema
from app.schemas.messages import (
    FileMessageRLSchema,
    MessageCSchema,
    MessageRLSchema,
    UserMessageRLSchema,
)
from app.utils.file_streamer import FileStreamer


class ChatsService:
    def __init__(
        self,
        db_session: AsyncSession,
        user_uid: int,
    ) -> None:
        self.db_session = db_session
        self.user_uid = user_uid

    async def create_chat(
        self,
    ) -> ChatLSchema:
        chat = Chat()
        self.db_session.add(chat)
        await self.db_session.commit()
        return ChatLSchema.model_validate(chat, from_attributes=True)

    @staticmethod
    def to_chat_rl_schema(
        chat: Chat,
    ) -> ChatRSchema:
        return ChatRSchema(
            uid=chat.uid,
            email=chat.email,
            first_name=chat.first_name,
            last_name=chat.last_name,
            patronymic_name=chat.patronymic_name,
            phone_number=chat.phone_number,
            rating=chat.rating,
        )

    async def get_chats_list(
        self,
    ) -> list[ChatLSchema]:
        return [
            ChatLSchema.model_validate(user, from_attributes=True)
            async for user in await self.db_session.stream_scalars(select(Chat))
        ]

    async def get_chat(
        self,
        chat_uid: int,
    ) -> ChatRSchema | None:
        chat = await self.get_chat_or_none(chat_uid)
        if not chat:
            return None
        return self.to_chat_rl_schema(chat)

    async def get_chat_messages(
        self,
        chat_uid: int,
        limit: int = 10,
        offset: int = 0,
    ) -> list[MessageRLSchema]:
        stmt = (
            select(Message)
            .where(Message.chat_uid == chat_uid)
            .options(
                joinedload(Message.files),
                joinedload(Message.user),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.db_session.execute(stmt)
        return [
            MessageRLSchema(
                uid=msg.uid,
                text=msg.text,
                files=[
                    FileMessageRLSchema(uid=f.uid, name=f.name, mime_type=f.mime_type)
                    for f in msg.files
                ],
                user=UserMessageRLSchema(
                    uid=msg.user.uid,
                    email=msg.user.email,
                    first_name=msg.user.first_name,
                    last_name=msg.user.last_name,
                    patronymic_name=msg.user.patronymic_name,
                )
                if msg.user
                else None,
                created_at=msg.created_at,
            )
            for msg in result.unique().scalars()
        ]

    async def download_message_file(
        self,
        file_uid: int,
    ) -> FileStreamer | None:
        file = await self.db_session.get(MessageFile, file_uid)
        if not file:
            return None
        return FileStreamer(file.path, mime_type=file.mime_type)

    async def get_chat_or_none(
        self,
        chat_uid: int,
    ) -> Chat | None:
        stmt = select(Chat).where(Chat.uid == chat_uid)
        chat = await self.db_session.scalar(stmt)
        return chat

    async def create_message(
        self,
        chat_uid: int,
        schema: MessageCSchema,
    ) -> None:
        message = Message(
            chat_uid=chat_uid,
            text=schema.text,
            files=[],
        )
        self.db_session.add(message)

        files_paths: list[Path] = []
        if schema.files:
            try:
                for f in schema.files:
                    if not f.size or f.size > 20 * 1024 * 1024:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="File size must be less than 20MB",
                        )
                    file_path = settings.FILES_PATH / f"{uuid4()}_{f.filename}"
                    files_paths.append(file_path)
                    content = await f.read()
                    mime = magic.Magic(mime=True)
                    mime_type = mime.from_buffer(content)
                    await file_path.write_bytes(content)
                    message.files.append(
                        MessageFile(
                            name=f.filename,
                            path=file_path,
                            mime_type=mime_type,
                        )
                    )
            except:
                for p in files_paths:
                    await p.unlink()
                raise
        await self.db_session.commit()
