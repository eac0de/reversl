from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from .permission import Permission


class User(Base):
    __tablename__ = "users"

    uid: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="User ID",
    )
    first_name: Mapped[str | None] = mapped_column(
        String(64),
        comment="User first name",
    )
    last_name: Mapped[str | None] = mapped_column(
        String(64),
        comment="User last name",
    )
    patronymic_name: Mapped[str | None] = mapped_column(
        String(64),
        comment="User patronymic name",
    )
    email: Mapped[EmailStr] = mapped_column(
        String(128),
        comment="User email",
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(64),
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
