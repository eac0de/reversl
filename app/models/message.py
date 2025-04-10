from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.typess import utcdatetime

from . import Base

if TYPE_CHECKING:
    from .chat import Chat


class Message(Base):
    __tablename__ = "messages"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Message id",
    )
    chat_uid: Mapped[int] = mapped_column(
        ForeignKey("chats.uid"),
        comment="Chat id",
    )
    text: Mapped[str] = mapped_column(
        String(1000),
    )
    created_at: Mapped[utcdatetime] = mapped_column(
        String(50),
    )
    user_uid: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.uid"),
        comment="User id",
    )

    chat: Mapped["Chat"] = relationship(
        back_populates="messages",
    )
