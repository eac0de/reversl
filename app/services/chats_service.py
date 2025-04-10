from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat
from app.schemas.chats import ChatLSchema, ChatRSchema
from app.schemas.messages import MessageRLSchema


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
        chat = await self.get_chat_or_none(chat_uid)
        if not chat:
            return None
        return self.to_chat_rl_schema(chat)

    async def get_chat_or_none(
        self,
        chat_uid: int,
    ) -> Chat | None:
        stmt = select(Chat).where(Chat.uid == chat_uid)
        return await self.db_session.scalar(stmt)
