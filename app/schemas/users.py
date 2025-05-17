from pydantic import BaseModel, EmailStr, Field

from app.models.permission import PermissionCode
from app.schemas.common import WithEmail, WithFullName, WithPhoneNumber


class UserCSchema(BaseModel):
    email: EmailStr = Field(
        title="User email",
    )
    password: str = Field(
        title="User password",
    )


class UserUSchema(
    WithFullName,
    WithEmail,
    WithPhoneNumber,
):
    pass


class UserRSchema(WithFullName, WithPhoneNumber):
    uid: int = Field(
        title="User ID",
    )
    email: EmailStr = Field(
        title="User email",
    )


class PermissionCodesSchema(BaseModel):
    permission_codes: set[PermissionCode] = Field(
        default_factory=set,
        title="User permissions",
    )


class UserRSchemaWithPermissions(
    UserRSchema,
    PermissionCodesSchema,
):
    pass


class UserLSchema(BaseModel):
    model_config = {
        "from_attributes": True,
    }
    uid: int = Field(
        title="User ID",
    )
