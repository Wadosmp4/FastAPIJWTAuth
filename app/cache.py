from aioredis import Redis

from app.config import config
from app.constants import REVOKED

redis_client = Redis(host=config.REDIS_HOST,
                     port=config.REDIS_PORT,
                     decode_responses=True,
                     password=config.REDIS_PASSWORD)


async def token_in_deny_list(jti: str):
    entry = await redis_client.get(jti)
    return entry and entry == REVOKED
