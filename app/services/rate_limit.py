from redis.asyncio import Redis

from app.core.config import settings

redis = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


async def check_rate_limit(
    identity: str,
    limit: int = 30,
    window_seconds: int = 60,
) -> bool:
    key = f"rag:rate:{identity}"

    async with redis.pipeline(transaction=True) as pipe:
        pipe.incr(key)
        pipe.ttl(key)
        count, ttl = await pipe.execute()

    if ttl == -1:
        await redis.expire(key, window_seconds)

    return count <= limit