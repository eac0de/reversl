from typing import Annotated

from fa_filter import Filter, Manual
from fastapi import Query

from app.models.user import User


class UsersFilter(Filter):
    uid__neq: int | None = Query(
        default=None,
        gt=0,
        description="User ID to exclude",
        include_in_schema=False,
    )
    user_uid: Annotated[int | None, Manual] = Query(
        default=None,
        gt=0,
        description="User ID to filter by",
    )

    limit: Annotated[int, Manual] = Query(
        default=30,
        gt=0,
        le=100,
        description="Maximum number of items to return",
    )

    class Settings(Filter.Settings):
        model = User
