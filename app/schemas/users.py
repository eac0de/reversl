from pydantic import BaseModel, EmailStr, Field

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


class UserRSchemaWithPermissions(UserRSchema):
    permissions: list[str] = Field(
        default_factory=list,
        title="User permissions",
    )


class UserLSchema(WithFullName):
    uid: int = Field(
        title="User ID",
    )
    email: EmailStr = Field(
        title="User email",
    )
