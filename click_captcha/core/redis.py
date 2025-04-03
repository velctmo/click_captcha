import json
import logging
from typing import AnyStr, Optional, TypeVar, Union

import aioredis

from click_captcha.core.config import settings

logger = logging.getLogger(__name__)
RedisKey = TypeVar("RedisKey", str, bytes)
RedisValue = Union[AnyStr, float, int]


class RedisManager:
    """Redis manager responsible for all Redis operations in the application."""

    # Redis connection pool
    _client: aioredis.Redis = aioredis.from_url(settings.REDIS_URL)

    @classmethod
    async def set(cls, key: str, data: dict, ttl: int = 0) -> bool:
        """
        Store JSON data in Redis.

        Args:
            key: Redis key
            data: Dictionary data to store
            ttl: Expiration time in seconds (0 for no expiration)

        Returns:
            bool: Success status
        """
        json_data = json.dumps(data)
        return await cls._client.set(key, json_data, ex=ttl)

    @classmethod
    async def get(cls, key: str) -> Optional[dict]:
        """
        Get JSON data from Redis.

        Args:
            key: Redis key

        Returns:
            Optional[dict]: Retrieved data or None if key doesn't exist
        """
        data = await cls._client.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON data for key: {key}")
        return None

    @classmethod
    async def delete(cls, key: str) -> bool:
        """
        Delete data from Redis.

        Args:
            key: Redis key

        Returns:
            bool: Whether the key was deleted
        """
        return bool(await cls._client.delete(key))
