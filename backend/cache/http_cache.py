"""
HTTP Response Caching Middleware.
Provides caching at the API/HTTP layer for FastAPI endpoints.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json
import hashlib
from typing import Dict, Any, Optional
import time

from . import redis_client
from ..utils.logging.logger import get_logger

logger = get_logger(__name__)

class HttpResponseCacheMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for caching HTTP responses.
    Caches GET responses for configurable paths and durations.
    """
    
    def __init__(
        self, 
        app, 
        cacheable_paths: Optional[Dict[str, int]] = None,
        enable_cache_header: bool = True
    ):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application
            cacheable_paths: Dictionary mapping paths to TTL in seconds
            enable_cache_header: Whether to include cache headers in response
        """
        super().__init__(app)
        self.enable_cache_header = enable_cache_header
        
        # Default cacheable paths if none provided
        self.cacheable_paths = cacheable_paths or {
            "/api/leads": 30,                # 30 seconds for lead lists
            "/api/leads/prioritized": 60,    # 60 seconds for prioritized leads
            "/api/leads/branch/": 45,        # 45 seconds for branch leads
            "/health": 300,                  # 5 minutes for health check
        }
        
        logger.info(f"HTTP Cache Middleware initialized with {len(self.cacheable_paths)} cacheable paths")
    
    async def dispatch(self, request: Request, call_next):
        """Process an incoming request and apply caching if applicable."""
        # Skip caching if Redis client is not available
        if not redis_client:
            logger.warning("Redis client not available, skipping HTTP response caching")
            return await call_next(request)
            
        # Skip non-GET requests - only cache GET requests
        if request.method != "GET":
            return await call_next(request)
            
        # Check if this path should be cached
        path = request.url.path
        cache_ttl = None
        
        for cacheable_path, ttl in self.cacheable_paths.items():
            if path.startswith(cacheable_path):
                cache_ttl = ttl
                break
                
        if not cache_ttl:
            return await call_next(request)
            
        # Create unique cache key based on path and parameters
        query_string = str(request.query_params)
        auth_header = request.headers.get("authorization", "")
        # Use hashed auth header to differentiate between users but protect sensitive info
        auth_hash = hashlib.md5(auth_header.encode()).hexdigest() if auth_header else "noauth"
        cache_key = f"http:{hashlib.md5(f'{path}:{query_string}:{auth_hash}'.encode()).hexdigest()}"
        
        start_time = time.time()
        
        # Check if response is already cached
        cached_response = await redis_client.get(cache_key)
        if cached_response:
            try:
                data = json.loads(cached_response)
                response = Response(
                    content=data["content"],
                    status_code=data["status_code"],
                    headers=data["headers"],
                    media_type=data["media_type"]
                )
                
                # Add cache hit header if enabled
                if self.enable_cache_header:
                    response.headers["X-Cache"] = "HIT"
                    response.headers["X-Cache-Time"] = f"{(time.time() - start_time):.6f}"
                
                logger.debug(f"Cache hit for {path} ({cache_key})")
                return response
            except Exception as e:
                logger.error(f"Error deserializing cached response: {str(e)}")
                # Fall through to non-cached path
        
        # If not in cache, proceed with request handling
        response = await call_next(request)
        
        # Cache successful responses only
        if 200 <= response.status_code < 300:
            try:
                # Get response body
                body_bytes = b""
                async for chunk in response.body_iterator:
                    body_bytes += chunk
                
                # Cache the response
                cache_data = {
                    "content": body_bytes.decode(),
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type
                }
                
                await redis_client.setex(cache_key, cache_ttl, json.dumps(cache_data))
                
                # Create a new response with the captured body
                response = Response(
                    content=body_bytes,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
                
                # Add cache miss header if enabled
                if self.enable_cache_header:
                    response.headers["X-Cache"] = "MISS"
                    response.headers["X-Cache-TTL"] = str(cache_ttl)
                
                logger.debug(f"Cached response for {path} ({cache_key}), TTL: {cache_ttl}s")
            except Exception as e:
                logger.error(f"Error caching response: {str(e)}")
                # Return original response if caching fails
        
        return response 