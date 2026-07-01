"""
Redis connection and caching utilities
"""

from typing import Optional, Any
import json

import redis.asyncio as redis
from redis.asyncio import Redis

from app.config import settings


# Global Redis client
_redis_client: Optional[Redis] = None


async def get_redis_client() -> Redis:
    """Get or create Redis client."""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    return _redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


class CacheService:
    """Redis caching service."""
    
    def __init__(self, client: Redis):
        self.client = client
        self.default_ttl = settings.REDIS_CACHE_TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        return await self.client.set(key, value, ex=ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        return await self.client.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return await self.client.exists(key) > 0
    
    async def incr(self, key: str) -> int:
        """Increment counter."""
        return await self.client.incr(key)
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on key."""
        return await self.client.expire(key, ttl)
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache."""
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set_json(
        self,
        key: str,
        value: dict,
        ttl: Optional[int] = None
    ) -> bool:
        """Set JSON value in cache."""
        return await self.set(key, json.dumps(value), ttl)


async def get_cache_service() -> CacheService:
    """Get cache service instance."""
    client = await get_redis_client()
    return CacheService(client)
