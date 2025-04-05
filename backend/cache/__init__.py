"""
Cache module for the application.
Provides caching utilities at different layers of the application.
"""

__all__ = ["redis_client", "setup_redis", "get_redis_client"]

import redis.asyncio as redis
from ..utils.logging.logger import get_logger
import os

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
        
        # Store Redis URL for potential reconnections
        os.environ["_REDIS_INTERNAL_URL"] = redis_url
        
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
    
    # If client exists, check if it's still connected
    if redis_client is not None:
        try:
            # Quick check that the client is still active
            # This is a non-blocking check that doesn't send a command
            if redis_client.connection_pool.connection_kwargs.get('host'):
                return redis_client
        except Exception:
            # If any error occurs, try to reinitialize
            redis_client = None
    
    # If we get here, we need to initialize or reinitialize
    if redis_client is None:
        # Try to get the URL from environment if available
        redis_url = os.environ.get("_REDIS_INTERNAL_URL", "redis://localhost:6379/0")
        logger.warning(f"Redis client not initialized. Attempting to connect with URL: {redis_url}")
        try:
            # Try to initialize with saved or default settings
            redis_client = redis.Redis.from_url(redis_url)
            logger.info(f"Redis client reinitialized with URL: {redis_url}")
            return redis_client
        except Exception as e:
            logger.error(f"Failed to reinitialize Redis client: {str(e)}")
            return None
    
    return redis_client 