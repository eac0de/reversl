import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

phone_number_pattern = re.compile(r"^(\+7|8|7)\d{10}$")


class WithPhoneNumber(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )
    phone_number: str | None = Field(
        max_length=12,
        min_length=11,
        default=None,
        title="User phone number",
    )

    @field_validator("phone_number", mode="before")
    def validate_phone_number(cls, value: str | None) -> str | None:
        if not value:
            return None
        if not phone_number_pattern.match(value):
            raise ValueError(
                "Phone number must start with 7, +7 or 8 and contain 10 digits",
            )
        if value[0] == "8":
            value = f"+7{value[1:]}"
        elif value[0] != "+":
            value = f"+{value}"
        return value


class WithEmail(BaseModel):
    email: EmailStr | None = Field(
        default=None,
        title="User email",
    )


class WithFullName(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
        str_max_length=64,
    )
    first_name: str | None = Field(
        default=None,
        title="User first name",
    )
    last_name: str | None = Field(
        default=None,
        title="User last name",
    )
    patronymic_name: str | None = Field(
        default=None,
        title="User patronymic name",
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''} {self.patronymic_name or ''}".strip()
