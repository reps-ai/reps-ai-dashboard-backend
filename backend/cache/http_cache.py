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
import logging

from . import get_redis_client
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
        enable_cache_header: bool = True,
        debug_log_level: int = logging.DEBUG  # Allow customizing the debug log level
    ):
        """
        Initialize the middleware.
        
        Args:
            app: FastAPI application
            cacheable_paths: Dictionary mapping paths to TTL in seconds
            enable_cache_header: Whether to include cache headers in response
            debug_log_level: Log level for detailed cache logs
        """
        super().__init__(app)
        self.enable_cache_header = enable_cache_header
        self.debug_log_level = debug_log_level
        
        # Default cacheable paths if none provided
        self.cacheable_paths = cacheable_paths or {
            "/api/leads": 300,                # 5 minutes for lead lists
            "/api/leads/prioritized": 600,    # 10 minutes for prioritized leads
            "/api/leads/branch/": 300,        # 5 minutes for branch leads
            "/health": 1800,                  # 30 minutes for health check
        }
        
        # Debug stats for monitoring
        self.stats = {
            "hits": 0,
            "misses": 0,
            "uncacheable": 0,
            "errors": 0,
            "last_request_time": None,
            "last_hit_time": None,
            "last_hit_path": None
        }
        
        logger.info(f"HTTP Cache Middleware initialized with {len(self.cacheable_paths)} cacheable paths")
        
        # Log the cacheable paths for debugging
        for path, ttl in self.cacheable_paths.items():
            logger.debug(f"Cacheable path: {path} with TTL: {ttl}s")
    
    async def dispatch(self, request: Request, call_next):
        """Process an incoming request and apply caching if applicable."""
        start_time = time.time()
        path = request.url.path
        method = request.method
        
        # Get Redis client
        redis_client = get_redis_client()
        
        # Skip caching if Redis client is not available
        if not redis_client:
            logger.warning(f"Redis client not available, skipping HTTP response caching for {method} {path}")
            self.stats["uncacheable"] += 1
            return await call_next(request)
            
        # Skip non-GET requests - only cache GET requests
        if method != "GET":
            logger.debug(f"Skipping cache for non-GET request: {method} {path}")
            self.stats["uncacheable"] += 1
            return await call_next(request)
            
        # Check if this path should be cached
        cache_ttl = None
        
        for cacheable_path, ttl in self.cacheable_paths.items():
            if path.startswith(cacheable_path):
                cache_ttl = ttl
                break
                
        if not cache_ttl:
            logger.debug(f"Path not cacheable: {path}")
            self.stats["uncacheable"] += 1
            return await call_next(request)
        
        # Create unique cache key based on path and parameters
        query_string = str(request.query_params)
        auth_header = request.headers.get("authorization", "")
        # Use hashed auth header to differentiate between users but protect sensitive info
        auth_hash = hashlib.md5(auth_header.encode()).hexdigest() if auth_header else "noauth"
        cache_key = f"http:{hashlib.md5(f'{path}:{query_string}:{auth_hash}'.encode()).hexdigest()}"
        
        logger.debug(f"Cache key for {path}: {cache_key}")
        logger.log(self.debug_log_level, f"Full request info - Path: {path}, Query: {query_string}, Auth hash: {auth_hash[:8]}...")
        
        # Check if response is already cached
        cached_response = None
        try:
            cached_response = await redis_client.get(cache_key)
        except Exception as e:
            logger.error(f"Error fetching cache key {cache_key}: {str(e)}")
            self.stats["errors"] += 1
            
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
                
                # Update stats
                self.stats["hits"] += 1
                self.stats["last_hit_time"] = time.time()
                self.stats["last_hit_path"] = path
                
                logger.info(f"Cache HIT for {method} {path} ({cache_key}) - {(time.time() - start_time):.6f}s")
                return response
            except Exception as e:
                logger.error(f"Error deserializing cached response for {path}: {str(e)}")
                self.stats["errors"] += 1
                # Fall through to non-cached path
        
        # If not in cache, proceed with request handling
        try:
            logger.info(f"Cache MISS for {method} {path} - fetching from source")
            response = await call_next(request)
            process_time = time.time() - start_time
            
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
                    
                    # Update stats
                    self.stats["misses"] += 1
                    self.stats["last_request_time"] = time.time()
                    
                    logger.info(f"Cached response for {method} {path} ({cache_key}), TTL: {cache_ttl}s, time: {process_time:.6f}s")
                except Exception as e:
                    logger.error(f"Error caching response for {path}: {str(e)}")
                    self.stats["errors"] += 1
                    # Return original response if caching fails
            else:
                logger.debug(f"Not caching non-success response ({response.status_code}) for {path}")
                
        except Exception as e:
            logger.error(f"Error processing request for {path}: {str(e)}")
            self.stats["errors"] += 1
            raise
        
        return response
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache operation."""
        total_requests = self.stats["hits"] + self.stats["misses"] + self.stats["uncacheable"]
        
        # Calculate hit rate if there are cacheable requests
        hit_rate = 0
        if (self.stats["hits"] + self.stats["misses"]) > 0:
            hit_rate = self.stats["hits"] / (self.stats["hits"] + self.stats["misses"])
        
        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "hit_rate_percent": f"{hit_rate * 100:.2f}%"
        } 