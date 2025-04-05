"""
Cache module for the application.
Provides caching utilities at different layers of the application.
"""

__all__ = ["redis_client", "setup_redis", "get_redis_client"]

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
        
    Returns:
        Redis client instance
    """
    global redis_client
    try:
        redis_client = redis.Redis.from_url(redis_url)
        # Test connection immediately to ensure it's working
        logger.info(f"Redis client initialized with URL: {redis_url}")
        return redis_client
    except Exception as e:
        logger.error(f"Failed to initialize Redis client: {str(e)}")
        redis_client = None
        logger.warning("Caching will be disabled due to Redis connection failure")
        raise

def get_redis_client():
    """
    Get the Redis client instance.
    
    Returns:
        Redis client instance or None if not initialized
    """
    global redis_client
    if redis_client is None:
        logger.warning("Redis client not initialized. Attempting to use default connection.")
        try:
            # Try to initialize with default settings if not already done
            redis_client = redis.Redis.from_url("redis://localhost:6379/0")
            logger.info("Redis client initialized with default URL")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client with default URL: {str(e)}")
    return redis_client 