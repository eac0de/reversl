from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.DATABASE_DSN, echo=False)
get_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@asynccontextmanager
async def with_commit(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    try:
        yield
        await db_session.commit()
    except Exception:
        await db_session.rollback()
        raise
