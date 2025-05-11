from pydantic import BaseModel, Field

from app.schemas.common import WithEmail, WithFullName, WithPhoneNumber


class ChatRSchema(
    WithFullName,
    WithEmail,
    WithPhoneNumber,
):
    uid: int = Field(
        title="Chat ID",
    )
    rating: int | None = Field(
        default=None,
        title="Chat rating",
    )


class ChatLSchema(BaseModel):
    uid: int = Field(
        title="Chat ID",
    )
