from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from .user import User


class PermissionCode(str, Enum):
    C_USER = "C_USER"
    R_USER = "R_USER"
    U_USER = "U_USER"
    D_USER = "D_USER"

    C_MESSAGE = "C_MESSAGE"
    R_MESSAGE = "R_MESSAGE"
    U_MESSAGE = "U_MESSAGE"
    D_MESSAGE = "D_MESSAGE"

    R_CHAT = "R_CHAT"
    U_CHAT = "U_CHAT"
    D_CHAT = "D_CHAT"

    C_PERMISSION = "C_PERMISSION"
    R_PERMISSION = "R_PERMISSION"
    U_PERMISSION = "U_PERMISSION"
    D_PERMISSION = "D_PERMISSION"


class Permission(Base):
    __tablename__ = "permissions"

    code: Mapped[PermissionCode] = mapped_column(
        primary_key=True,
        comment="Permission code",
    )
    user_uid: Mapped[UUID] = mapped_column(
        ForeignKey("users.uid"),
        primary_key=True,
        comment="User ID",
    )

    user: Mapped["User"] = relationship(
        back_populates="permissions",
    )
