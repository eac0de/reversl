from pydantic import BaseModel, Field


class ChatRSchema(BaseModel):
    uid: int = Field(
        title="Chat ID",
    )
    first_name: str | None = Field(
        default=None,
        title="Customer first name",
    )
    last_name: str | None = Field(
        default=None,
        title="Customer last name",
    )
    patronymic_name: str | None = Field(
        default=None,
        title="Chat patronymic name",
    )
    phone_number: str | None = Field(
        default=None,
        title="Chat phone number",
    )
    email: str | None = Field(
        default=None,
        title="Chat email",
    )
    rating: int | None = Field(
        default=None,
        title="Chat rating",
    )


class ChatLSchema(BaseModel):
    uid: int = Field(
        title="Chat ID",
    )
