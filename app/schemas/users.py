from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCSchema:
    email: EmailStr = Field(
        title="User email",
    )
    password: str = Field(
        title="User password",
    )


class UserRSchema(BaseModel):
    uid: UUID = Field(
        title="User ID",
    )
    email: EmailStr = Field(
        title="User email",
    )
    first_name: str | None = Field(
        title="User first name",
    )
    last_name: str | None = Field(
        title="User last name",
    )
    patronymic_name: str | None = Field(
        title="User patronymic name",
    )
    phone_number: str | None = Field(
        title="User phone number",
    )
    permissions: list[str] = Field(
        default_factory=list,
        title="User permissions",
    )
