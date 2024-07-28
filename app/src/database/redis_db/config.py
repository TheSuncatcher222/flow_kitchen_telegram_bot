from redis import Redis

from config.config import settings

db_redis: Redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_CACHE,
    decode_responses=True,
)
