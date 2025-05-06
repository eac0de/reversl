from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.typess import utcdatetime

from . import Base

if TYPE_CHECKING:
    from .chat import Chat
    from .message_file import MessageFile
    from .user import User


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (PrimaryKeyConstraint("uid", name="messages_pkey"),)

    uid: Mapped[int] = mapped_column(
        autoincrement=True,
        comment="Message ID",
    )
    chat_uid: Mapped[int] = mapped_column(
        ForeignKey(
            "chats.uid",
            ondelete="CASCADE",
            name="messages_chat_uid_fkey",
        ),
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
    user_uid: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.uid",
            name="messages_user_uid_fkey",
        ),
        default=None,
        comment="User ID",
    )

    chat: Mapped["Chat"] = relationship(
        back_populates="messages",
    )
    user: Mapped["User | None"] = relationship(
        back_populates="messages",
    )
    files: Mapped[list["MessageFile"]] = relationship(
        back_populates="message",
    )
