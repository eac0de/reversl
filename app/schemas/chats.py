from pydantic import BaseModel, Field

from app.schemas.common import WithEmail, WithFullName, WithPhoneNumber


class ChatUSchema(
    WithFullName,
    WithEmail,
    WithPhoneNumber,
):
    rating: int | None = Field(
        default=None,
        title="Chat rating",
    )


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
    model_config = {
        "from_attributes": True,
    }
    uid: int = Field(
        title="Chat ID",
    )
