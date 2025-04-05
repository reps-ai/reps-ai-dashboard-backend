"""
Service-layer caching utilities.
Provides decorators for caching service method results.
"""

import json
import hashlib
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
import time

from . import get_redis_client
from ..utils.logging.logger import get_logger
from ..utils.serialization import serialize_to_json, deserialize_from_json

logger = get_logger(__name__)

def service_cache(namespace: str, ttl: int = 60):
    """
    Decorator to cache service method results.
    
    Args:
        namespace: Cache namespace (e.g., "lead", "user")
        ttl: Time-to-live in seconds
    
    Returns:
        Decorated function with caching
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get Redis client
            redis_client = get_redis_client()
            
            # Skip caching if Redis client is not available
            if not redis_client:
                logger.warning(f"Redis client not available, skipping cache for {func.__name__}")
                return await func(*args, **kwargs)
                
            # Skip caching for write operations or when explicitly requested
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
            try:
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    try:
                        logger.debug(f"Cache hit for {func.__name__} ({cache_key}), " +
                                    f"time: {(time.time() - start_time):.6f}s")
                        return deserialize_from_json(cached_data)
                    except Exception as e:
                        logger.error(f"Error deserializing cached data: {str(e)}")
                        # Fall through to non-cached path
            except Exception as e:
                logger.error(f"Error retrieving from cache: {str(e)}")
                # Fall through to non-cached path
                
            # Execute function if not in cache
            result = await func(*args, **kwargs)
            
            # Cache result if it's valid (not None)
            if result is not None:
                try:
                    # Use custom serialization that handles UUIDs
                    await redis_client.setex(cache_key, ttl, serialize_to_json(result))
                    logger.debug(f"Cached result for {func.__name__} ({cache_key}), TTL: {ttl}s")
                except Exception as e:
                    logger.error(f"Error caching result: {str(e)}")
                
            return result
        return wrapper
    return decorator 