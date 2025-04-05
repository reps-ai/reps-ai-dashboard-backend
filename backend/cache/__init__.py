"""
Cache module for the application.
Provides caching utilities at different layers of the application.
"""

__all__ = ["redis_client", "setup_redis"]

import redis.asyncio as redis
from ..utils.logging.logger import get_logger

logger = get_logger(__name__)

# Redis client instance to be initialized during app startup
redis_client = None

def setup_redis(redis_url: str = "redis://localhost:6379/0"):
    """
    Initialize the Redis client.
    Should be called during application startup.
    
    Args:
        redis_url: Redis connection URL
    """
    global redis_client
    try:
        redis_client = redis.Redis.from_url(redis_url)
        logger.info(f"Redis client initialized with URL: {redis_url}")
        return redis_client
    except Exception as e:
        logger.error(f"Failed to initialize Redis client: {str(e)}")
        raise 