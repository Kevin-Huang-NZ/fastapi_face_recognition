from aioredis import Redis, from_url

from core.config import settings


async def init_redis_pool() -> Redis:
    if settings.USE_REDIS_SENTINEL:
        pass
    else:
        redis = await from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            db=settings.REDIS_DB,
        )
    return redis