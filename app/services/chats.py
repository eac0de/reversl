from uuid import uuid4

import magic
from anyio import Path
from fastapi import HTTPException, status
from sqlalchemy import ScalarResult, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.admin_panel.filters.messages import MessagesFilter
from app.config import settings
from app.models.chat import Chat
from app.models.message import Message
from app.models.message_file import MessageFile
from app.models.user import User
from app.schemas.chats import ChatLSchema, ChatRSchema, ChatUSchema
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
    ) -> None:
        self.db_session = db_session

    async def create_chat(
        self,
    ) -> ChatLSchema:
        chat = Chat()
        self.db_session.add(chat)
        await self.db_session.flush()
        return ChatLSchema.model_validate(chat, from_attributes=True)

    async def get_chats_list(
        self,
    ) -> list[ChatLSchema]:
        return [
            ChatLSchema.model_validate(user, from_attributes=True)
            async for user in await self.db_session.stream_scalars(select(Chat))
        ]

    async def update_chat(
        self,
        chat: Chat,
        schema: ChatUSchema,
    ) -> Chat:
        await self.db_session.execute(
            update(Chat)
            .where(Chat.uid == chat.uid)
            .values(**schema.model_dump(exclude_unset=True))
        )
        await self.db_session.flush()
        await self.db_session.refresh(chat)
        return chat

    async def get_messages_list(
        self,
        chat_uid: int,
        messages_filter: MessagesFilter,
    ) -> ScalarResult[Message]:
        stmt = messages_filter(
            select(Message)
            .where(Message.chat_uid == chat_uid)
            .options(
                joinedload(Message.files),
            )
            .order_by(Message.created_at.desc())
        )
        result = await self.db_session.execute(stmt)
        return result.unique().scalars()

    async def download_message_file(
        self,
        chat_uid: int,
        file_uid: int,
    ) -> FileStreamer:
        stmt = (
            select(MessageFile)
            .join(MessageFile.message)
            .where(
                Message.chat_uid == chat_uid,
                MessageFile.uid == file_uid,
            )
        )
        file = await self.db_session.scalar(stmt)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        return FileStreamer(
            filename=file.name,
            filepath=file.path,
            mime_type=file.mime_type,
        )

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
        current_user: User | None = None,
    ) -> Message:
        message = Message(
            chat_uid=chat_uid,
            text=schema.text,
            files=[],
            user=current_user,
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
        return message

    @staticmethod
    def to_chat_r_schema(
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

    @staticmethod
    def to_message_rl_schema(
        message: Message,
    ) -> MessageRLSchema:
        return MessageRLSchema(
            uid=message.uid,
            text=message.text,
            files=[
                FileMessageRLSchema(
                    uid=f.uid,
                    name=f.name,
                    mime_type=f.mime_type,
                )
                for f in message.files
            ],
            created_at=message.created_at,
            user=UserMessageRLSchema(
                uid=message.user.uid,
                email=message.user.email,
            )
            if message.user
            else None,
        )
