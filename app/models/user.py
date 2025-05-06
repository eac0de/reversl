from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from .message import Message
    from .permission import Permission


class User(Base):
    __tablename__ = "users"
    __table_args__ = (PrimaryKeyConstraint("uid", name="users_pkey"),)

    uid: Mapped[int] = mapped_column(
        autoincrement=True,
        comment="User ID",
    )
    first_name: Mapped[str | None] = mapped_column(
        String(64),
        default=None,
        comment="User first name",
    )
    last_name: Mapped[str | None] = mapped_column(
        String(64),
        default=None,
        comment="User last name",
    )
    patronymic_name: Mapped[str | None] = mapped_column(
        String(64),
        default=None,
        comment="User patronymic name",
    )
    email: Mapped[EmailStr] = mapped_column(
        String(128),
        comment="User email",
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(64),
        default=None,
        comment="User phone number",
    )
    password: Mapped[str] = mapped_column(
        String(64),
        comment="User password",
    )

    permissions: Mapped[list["Permission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="user",
    )
