from datetime import datetime, timezone, tzinfo
from typing import Self

from anyio import Path
from pydantic_core import core_schema
from sqlalchemy import String, TypeDecorator


class utcdatetime(datetime):
    @classmethod
    def _to_utc(cls, dt: datetime) -> Self:
        if dt.tzinfo and dt.tzinfo != timezone.utc:
            dt = dt - dt.utcoffset()  # type: ignore
        return super(utcdatetime, cls).__new__(
            cls,
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tzinfo=timezone.utc,
        )

    def __new__(cls, *args, **kwargs) -> Self:
        dt = datetime.__new__(datetime, *args, **kwargs)
        return cls._to_utc(dt)

    @classmethod
    def now(cls) -> Self:
        return super().now(timezone.utc)

    def strftime(
        self,
        fmt: str,
        tz: tzinfo | None = None,
    ) -> str:
        if tz is None:
            tz = timezone.utc
        return (
            datetime(
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second,
                self.microsecond,
                tzinfo=timezone.utc,
            )
            .astimezone(tz)
            .strftime(fmt)
        )

    @classmethod
    def __get_pydantic_core_schema__(cls, *_) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._to_utc,
            core_schema.datetime_schema(),
        )


class PathType(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return Path(value)
        return None

    def process_literal_param(self, value, dialect):
        if value is not None:
            return str(value)
        return None

    @property
    def python_type(self):
        return Path
