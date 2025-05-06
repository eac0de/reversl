from typing import TYPE_CHECKING

from anyio import Path
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.typess import PathType

from . import Base

if TYPE_CHECKING:
    from .message import Message


class MessageFile(Base):
    __tablename__ = "message_files"
    __table_args__ = (PrimaryKeyConstraint("uid", name="message_files_pkey"),)

    uid: Mapped[int] = mapped_column(
        autoincrement=True,
        comment="Message file ID",
    )
    name: Mapped[str] = mapped_column(
        String(256),
        comment="File name",
    )
    mime_type: Mapped[str] = mapped_column(
        String(256),
        comment="File MIME type",
    )
    path: Mapped[Path] = mapped_column(
        PathType(),
        comment="File path",
    )
    message_uid: Mapped[int] = mapped_column(
        ForeignKey(
            "messages.uid",
            ondelete="CASCADE",
            name="message_files_message_uid_fkey",
        ),
        comment="Message ID",
    )

    message: Mapped["Message"] = relationship(
        back_populates="files",
    )
