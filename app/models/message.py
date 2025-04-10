from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.typess import utcdatetime

from . import Base

if TYPE_CHECKING:
    from .chat import Chat
    from .message_file import MessageFile


class Message(Base):
    __tablename__ = "messages"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Message ID",
    )
    chat_uid: Mapped[int] = mapped_column(
        ForeignKey("chats.uid"),
        comment="Chat ID",
    )
    text: Mapped[str | None] = mapped_column(
        String(1024),
        default=None,
        comment="Message text",
    )
    created_at: Mapped[utcdatetime] = mapped_column(
        DateTime(timezone=True),
        default=utcdatetime.now,
        comment="Message created at",
    )
    user_uid: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.uid"),
        comment="User ID",
    )

    chat: Mapped["Chat"] = relationship(
        back_populates="messages",
    )
    files: Mapped[list["MessageFile"]] = relationship(
        back_populates="message",
    )
