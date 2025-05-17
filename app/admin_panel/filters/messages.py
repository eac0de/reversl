from typing import Annotated

from fa_filter import Filter, Manual
from fastapi import Query


class MessagesFilter(Filter):
    limit: Annotated[int, Manual] = Query(
        default=5,
        gt=0,
        le=100,
        description="Maximum number of items to return",
    )
