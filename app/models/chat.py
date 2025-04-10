from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from .message import Message


class Chat(Base):
    __tablename__ = "chats"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Chat id",
    )
    first_name: Mapped[str | None] = mapped_column(
        String(64),
        comment="Customer first name",
    )
    last_name: Mapped[str | None] = mapped_column(
        String(64),
        comment="Customer last name",
    )
    patrynomic_name: Mapped[str | None] = mapped_column(
        String(64),
        comment="Chat patronymic name",
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(64),
        comment="Chat phone number",
    )
    email: Mapped[str | None] = mapped_column(
        String(128),
        comment="Chat email",
    )
    rating: Mapped[int | None] = mapped_column(
        comment="Chat rating",
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat",
    )
