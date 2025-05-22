# redis_client.py
import redis.asyncio as redis
from pydantic import RedisDsn

redis_client: redis.Redis = None  # type: ignore


def init_redis(url: RedisDsn) -> None:
    global redis_client  # noqa: PLW0603

    redis_client = redis.from_url(
        url=str(url),
        decode_responses=True,
    )


def get_redis() -> redis.Redis:
    return redis_client
