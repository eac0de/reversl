from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
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

    R_PERMISSION = "R_PERMISSION"
    U_PERMISSION = "U_PERMISSION"


PERMISSION_GROUPS_MAP: dict[str, set[PermissionCode]] = {
    "User": {
        PermissionCode.R_USER,
        PermissionCode.U_USER,
        PermissionCode.D_USER,
    },
    "Message": {
        PermissionCode.C_MESSAGE,
        PermissionCode.R_MESSAGE,
        PermissionCode.U_MESSAGE,
        PermissionCode.D_MESSAGE,
    },
    "Chat": {
        PermissionCode.R_CHAT,
        PermissionCode.U_CHAT,
        PermissionCode.D_CHAT,
    },
    "Permission": {
        PermissionCode.R_PERMISSION,
        PermissionCode.U_PERMISSION,
    },
}


PERMISSION_CODE_TO_NAME_MAP: dict[PermissionCode, str] = {
    PermissionCode.C_USER: "Create user",
    PermissionCode.R_USER: "Read user",
    PermissionCode.U_USER: "Update user",
    PermissionCode.D_USER: "Delete user",
    PermissionCode.C_MESSAGE: "Create message",
    PermissionCode.R_MESSAGE: "Read message",
    PermissionCode.U_MESSAGE: "Update message",
    PermissionCode.D_MESSAGE: "Delete message",
    PermissionCode.R_CHAT: "Read chat",
    PermissionCode.U_CHAT: "Update chat",
    PermissionCode.D_CHAT: "Delete chat",
    PermissionCode.R_PERMISSION: "Read permission",
    PermissionCode.U_PERMISSION: "Update permission",
}


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (
        PrimaryKeyConstraint("code", "user_uid", name="permissions_pkey"),
    )

    code: Mapped[PermissionCode] = mapped_column(
        comment="Permission code",
    )
    user_uid: Mapped[int] = mapped_column(
        ForeignKey(
            "users.uid",
            ondelete="CASCADE",
            name="permissions_user_uid_fkey",
        ),
        comment="User ID",
    )

    user: Mapped["User"] = relationship(
        back_populates="permissions",
    )
