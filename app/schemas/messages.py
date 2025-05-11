from fastapi import UploadFile
from pydantic import BaseModel, Field, model_validator

from app.core.typess import utcdatetime
from app.schemas.common import WithFullName


class MessageCSchema(BaseModel):
    text: str | None = Field(
        default=None,
        title="Message text",
    )
    files: list[UploadFile] = Field(
        default_factory=list,
        title="Message files",
    )

    @model_validator(mode="after")
    def validate_message(self) -> "MessageCSchema":
        if self.text is not None:
            self.text = self.text.strip()
            if not self.text:
                self.text = None
        if not self.text and not self.files:
            raise ValueError("Message text or files must be provided.")
        return self


class FileMessageRLSchema(BaseModel):
    uid: int = Field(
        title="File ID",
    )
    name: str = Field(
        title="File name",
    )
    mime_type: str = Field(
        title="File MIME type",
    )


class UserMessageRLSchema(WithFullName):
    uid: int = Field(
        title="User ID",
    )
    email: str = Field(
        title="User email",
    )


class MessageRLSchema(BaseModel):
    uid: int = Field(
        title="Message ID",
    )
    text: str | None = Field(
        default=None,
        title="Message text",
    )
    files: list[FileMessageRLSchema] = Field(
        default_factory=list,
        title="Message files",
    )
    created_at: utcdatetime = Field(
        title="Message created at",
    )
    user: UserMessageRLSchema | None = Field(
        default=None,
        title="Message author",
    )
