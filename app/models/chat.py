from typing import TYPE_CHECKING

from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from .message import Message


class Chat(Base):
    __tablename__ = "chats"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Chat ID",
    )
    first_name: Mapped[str | None] = mapped_column(
        String(64),
        default=None,
        comment="Customer first name",
    )
    last_name: Mapped[str | None] = mapped_column(
        String(64),
        default=None,
        comment="Customer last name",
    )
    patrynomic_name: Mapped[str | None] = mapped_column(
        String(64),
        default=None,
        comment="Chat patronymic name",
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(64),
        default=None,
        comment="Chat phone number",
    )
    email: Mapped[str | None] = mapped_column(
        String(128),
        default=None,
        comment="Chat email",
    )
    rating: Mapped[int] = mapped_column(
        SmallInteger(),
        default=0,
        comment="Chat rating",
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat",
    )
