from typing import Annotated, Literal

from anyio import Path
from pydantic import BeforeValidator, EmailStr, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "reversl"
    MODE: Literal["DEV", "TEST", "PROD"] = "DEV"
    PROJECT_DIR: Path = Path(__file__).parent

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5454
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "reversl"

    REDIS_DSN: RedisDsn = RedisDsn("redis://localhost:6379/0")

    SECRET_KEY: str = "secret"

    REVERSL_FIRST_USER_EMAIL: EmailStr = "admin@admin.com"
    REVERSL_FIRST_USER_PASSWORD: str = "admin"

    REVERSL_URL_PREFIX: Annotated[str, BeforeValidator(lambda v: v.strip("/"))] = ""

    REVERSL_CSRF_TOKEN_KEY: str = "reversl-csrf-token"

    FILES_PATH: Path = Path(__file__).parent.parent.joinpath("data", "files")

    @property
    def DATABASE_DSN(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
