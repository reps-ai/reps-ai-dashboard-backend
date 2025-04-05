"""
Repository-layer caching utilities.
Provides decorators for caching database query results.
"""

import json
import hashlib
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
import time

from . import redis_client
from ..utils.logging.logger import get_logger

logger = get_logger(__name__)

def repository_cache(namespace: str, ttl: int = 60):
    """
    Decorator to cache repository method results.
    
    Args:
        namespace: Cache namespace (e.g., "lead_query", "user_query")
        ttl: Time-to-live in seconds
    
    Returns:
        Decorated function with caching
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if Redis client is not available
            if not redis_client:
                logger.warning(f"Redis client not available, skipping cache for {func.__name__}")
                return await func(*args, **kwargs)
                
            # Skip caching for write operations - they should invalidate cache instead
            write_prefixes = ("create_", "update_", "delete_", "add_", "remove_")
            if func.__name__.startswith(write_prefixes):
                # Execute the write operation
                result = await func(*args, **kwargs)
                
                # Try to invalidate related caches if possible
                entity_id = None
                
                # Look for entity ID in the result
                if result and isinstance(result, dict) and "id" in result:
                    entity_id = result["id"]
                # Or look in the first argument (typically entity_id)
                elif len(args) > 1 and args[1]:
                    entity_id = args[1]
                
                if entity_id:
                    # Get all keys in this namespace that might contain this ID
                    pattern = f"{namespace}:*{entity_id}*"
                    try:
                        keys = await redis_client.keys(pattern)
                        if keys:
                            await redis_client.delete(*keys)
                            logger.debug(f"Invalidated {len(keys)} cache keys for {func.__name__} with ID {entity_id}")
                    except Exception as e:
                        logger.error(f"Error invalidating cache: {str(e)}")
                
                return result
            
            # Skip caching when explicitly requested
            if kwargs.get("skip_cache", False):
                kwargs.pop("skip_cache", None)
                return await func(*args, **kwargs)
            
            # Build cache key from function name, args, and kwargs
            # Skip first arg (self) for instance methods
            cache_args = args[1:] if args and hasattr(args[0], "__class__") else args
            
            # Handle complex arguments by converting them to strings
            key_parts = [func.__name__]
            for arg in cache_args:
                if isinstance(arg, (dict, list)):
                    # Use stable representation for collections
                    arg_str = hashlib.md5(json.dumps(arg, sort_keys=True).encode()).hexdigest()
                else:
                    arg_str = str(arg)
                key_parts.append(arg_str)
            
            # Add sorted kwargs to ensure consistent keys
            for k, v in sorted(kwargs.items()):
                if k != "skip_cache":
                    if isinstance(v, (dict, list)):
                        v_str = hashlib.md5(json.dumps(v, sort_keys=True).encode()).hexdigest()
                    else:
                        v_str = str(v)
                    key_parts.append(f"{k}:{v_str}")
                    
            cache_key = f"{namespace}:{':'.join(key_parts)}"
            
            start_time = time.time()
            
            # Try to get from cache
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                try:
                    logger.debug(f"Cache hit for {func.__name__} ({cache_key}), " +
                                f"time: {(time.time() - start_time):.6f}s")
                    return json.loads(cached_data)
                except Exception as e:
                    logger.error(f"Error deserializing cached data: {str(e)}")
                    # Fall through to non-cached path
                
            # Execute function if not in cache
            result = await func(*args, **kwargs)
            
            # Cache result if it's valid (not None)
            if result is not None:
                try:
                    await redis_client.setex(cache_key, ttl, json.dumps(result))
                    logger.debug(f"Cached result for {func.__name__} ({cache_key}), TTL: {ttl}s")
                except Exception as e:
                    logger.error(f"Error caching result: {str(e)}")
                
            return result
        return wrapper
    return decorator 