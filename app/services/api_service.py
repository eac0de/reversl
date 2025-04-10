from uuid import uuid4

from anyio import Path
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import settings
from app.models.message import Message
from app.models.message_file import MessageFile
from app.schemas.messages import FileMessageRLSchema, MessageCSchema, MessageRLSchema
from app.utils.file_streamer import FileStreamer


class APIService:
    def __init__(
        self,
        db_session: AsyncSession,
        chat_id: int,
    ):
        self.db_session = db_session
        self.chat_id = chat_id

    async def create_message(
        self,
        schema: MessageCSchema,
    ) -> MessageRLSchema:
        message = Message(
            chat_uid=self.chat_id,
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
                    await file_path.write_bytes(await f.read())
                    message.files.append(
                        MessageFile(
                            name=f.filename,
                            path=file_path,
                        )
                    )
            except Exception:
                for p in files_paths:
                    await p.unlink()
                raise
        await self.db_session.commit()
        return await self.to_message_rl_schema(message)

    async def get_messages_list(
        self,
    ) -> list[MessageRLSchema]:
        stmt = (
            select(Message)
            .where(Message.chat_uid == self.chat_id)
            .options(
                joinedload(Message.files),
            )
        )
        result = await self.db_session.execute(stmt)
        return [await self.to_message_rl_schema(m) for m in result.unique().scalars()]

    async def download_message_file(
        self,
        file_uid: int,
    ) -> FileStreamer:
        stmt = (
            select(MessageFile)
            .join(MessageFile.message)
            .where(Message.chat_uid == self.chat_id, MessageFile.uid == file_uid)
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
        )

    async def to_message_rl_schema(
        self,
        message: Message,
    ) -> MessageRLSchema:

        return MessageRLSchema(
            uid=message.uid,
            text=message.text,
            files=[
                FileMessageRLSchema(
                    uid=f.uid,
                    name=f.name,
                )
                for f in message.files
            ],
            created_at=message.created_at,
        )
