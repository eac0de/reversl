from pydantic import BaseModel, EmailStr, Field


class UserCSchema(BaseModel):
    email: EmailStr = Field(
        title="User email",
    )
    password: str = Field(
        title="User password",
    )


class WithFullName(BaseModel):
    first_name: str | None = Field(
        title="User first name",
    )
    last_name: str | None = Field(
        title="User last name",
    )
    patronymic_name: str | None = Field(
        title="User patronymic name",
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''} {self.patronymic_name or ''}".strip()


class UserRSchema(WithFullName):
    uid: int = Field(
        title="User ID",
    )
    email: EmailStr = Field(
        title="User email",
    )
    phone_number: str | None = Field(
        title="User phone number",
    )
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
