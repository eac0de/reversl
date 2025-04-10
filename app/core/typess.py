from datetime import datetime, timezone, tzinfo
from typing import Self

from anyio import Path
from pydantic_core import core_schema
from sqlalchemy import String, TypeDecorator


class utcdatetime(datetime):
    @classmethod
    def _to_utc(cls, dt: datetime) -> Self:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        elif dt.tzinfo != timezone.utc:
            dt = dt.astimezone(timezone.utc)
        return dt  # type: ignore

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        return cls._to_utc(obj)

    @classmethod
    def now(cls) -> Self:
        return cls._to_utc(datetime.now(timezone.utc))

    @classmethod
    def fromisoformat(cls, date_string: str) -> Self:
        return cls._to_utc(datetime.fromisoformat(date_string))

    @classmethod
    def __get_pydantic_core_schema__(cls, *_) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._to_utc,
            core_schema.datetime_schema(),
        )

    def strftime_with_tz(
        self,
        fmt: str,
        tz: tzinfo,
    ) -> str:
        return self.astimezone(tz).strftime(fmt)


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
