from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.chat import Chat
from app.models.message import Message
from app.schemas.chats import ChatLSchema, ChatRSchema
from app.schemas.messages import FileMessageRLSchema, MessageRLSchema


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
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.db_session.execute(stmt)
        return [
            MessageRLSchema(
                uid=msg.uid,
                text=msg.text,
                files=[FileMessageRLSchema(uid=f.uid, name=f.name) for f in msg.files],
                created_at=msg.created_at,
            )
            for msg in result.unique().scalars()
        ]
    
    async def download_message_image(
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
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.db_session.execute(stmt)
        return [
            MessageRLSchema(
                uid=msg.uid,
                text=msg.text,
                files=[FileMessageRLSchema(uid=f.uid, name=f.name) for f in msg.files],
                created_at=msg.created_at,
            )
            for msg in result.unique().scalars()
        ]

    async def get_chat_or_none(
        self,
        chat_uid: int,
    ) -> Chat | None:
        stmt = select(Chat).where(Chat.uid == chat_uid)
        return await self.db_session.scalar(stmt)
