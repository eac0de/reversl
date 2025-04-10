from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from .permission import Permission


class User(Base):
    __tablename__ = "users"

    uid: Mapped[UUID] = mapped_column(
        primary_key=True,
        default_factory=uuid4,
        comment="User id",
    )
    first_name: Mapped[str] = mapped_column(
        String(64),
        comment="User first name",
    )
    last_name: Mapped[str] = mapped_column(
        String(64),
        comment="User last name",
    )
    patronymic_name: Mapped[str | None] = mapped_column(
        String(64),
        comment="User patronymic name",
    )
    email: Mapped[str] = mapped_column(
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
    )
