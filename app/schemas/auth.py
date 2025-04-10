from pydantic import BaseModel, Field


class LoginSchema(BaseModel):
    email: str = Field(
        title="User email",
    )
    password: str = Field(
        title="User password",
    )


class AccessTokenScheme(BaseModel):
    access_token: str = Field(
        title="Access token",
    )
