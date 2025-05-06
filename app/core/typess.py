from datetime import UTC, datetime, tzinfo
from typing import Any, Self

from anyio import Path
from pydantic_core import core_schema
from sqlalchemy import String, TypeDecorator
from sqlalchemy.engine.interfaces import Dialect


class utcdatetime(datetime):
    @classmethod
    def _to_utc(cls, dt: datetime) -> Self:
        if dt.tzinfo and dt.tzinfo != UTC:
            dt = dt - dt.utcoffset()  # type: ignore
        return super().__new__(
            cls,
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tzinfo=UTC,
        )

    def __new__(cls, *args, **kwargs) -> Self:  # type: ignore
        dt = datetime.__new__(datetime, *args, **kwargs)
        return cls._to_utc(dt)

    @classmethod
    def now(cls) -> Self:  # type: ignore
        return super().now(UTC)

    def strftime(
        self,
        fmt: str,
        tz: tzinfo | None = None,
    ) -> str:
        if tz is None:
            tz = UTC
        return (
            datetime(
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second,
                self.microsecond,
                tzinfo=UTC,
            )
            .astimezone(tz)
            .strftime(fmt)
        )

    @classmethod
    def __get_pydantic_core_schema__(cls, *_, **__) -> core_schema.CoreSchema:  # type: ignore
        return core_schema.no_info_after_validator_function(
            cls._to_utc,
            core_schema.datetime_schema(),
        )


class PathType(TypeDecorator[Path]):
    impl = String

    def process_bind_param(
        self,
        value: Path | None,
        dialect: Dialect,
    ) -> str | None:
        if value:
            return str(value)
        return None

    def process_result_value(
        self,
        value: Any | None,
        dialect: Dialect,
    ) -> Path | None:
        if value:
            return Path(value)
        return None

    def process_literal_param(
        self,
        value: Path | None,
        dialect: Dialect,
    ) -> str:
        return f"Path({value})"

    @property
    def python_type(self) -> type[Path]:
        return Path
