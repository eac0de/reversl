from pydantic import BaseModel, Field


class AccessTokenScheme(BaseModel):
    access_token: str = Field(
        title="Access token",
    )
