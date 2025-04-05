"""
API routes for cache diagnostics and testing.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import JSONResponse
import json
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.cache.diagnostic import (
    test_redis_connection,
    inspect_cache_keys,
    test_cache_layers,
    run_all_diagnostic_tests
)
from backend.cache import get_redis_client
from app.dependencies import get_current_user, User

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cache", tags=["Cache Diagnostics"])

@router.get("/health")
async def cache_health():
    """Check Redis connectivity and cache health."""
    result = await test_redis_connection()
    
    if not result["success"]:
        return JSONResponse(
            status_code=503,
            content=result
        )
    
    return result

@router.get("/inspect")
async def inspect_cache(
    pattern: str = "*",
    current_user: User = Depends(get_current_user)
):
    """
    Inspect cache keys matching a pattern.
    
    Args:
        pattern: Redis key pattern to match (default: "*")
    """
    result = await inspect_cache_keys(pattern)
    return result

@router.get("/test")
async def test_cache(
    current_user: User = Depends(get_current_user)
):
    """Test all cache layers with sample data."""
    result = await test_cache_layers()
    return result

@router.get("/diagnostic")
async def full_diagnostic(
    current_user: User = Depends(get_current_user)
):
    """Run a comprehensive diagnostic on the cache system."""
    result = await run_all_diagnostic_tests()
    return result

@router.get("/http-stats")
async def http_cache_stats(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics for the HTTP cache middleware.
    Shows hit rates, miss counts, and other performance metrics.
    """
    try:
        # Check if middleware reference is stored in app.state
        if hasattr(request.app.state, "http_cache_middleware"):
            http_cache_middleware = request.app.state.http_cache_middleware
            logger.info("Found HTTP middleware in app.state")
        else:
            logger.warning("HTTP cache middleware not found in app.state")
            return {
                "error": "HTTP cache middleware not found",
                "message": "The HttpResponseCacheMiddleware is not stored in app.state",
                "recommendation": "Ensure the middleware is properly initialized and stored in app.state"
            }
        
        # Get stats from the middleware
        stats = await http_cache_middleware.get_stats()
        
        # Add additional information
        stats["cacheable_paths"] = http_cache_middleware.cacheable_paths
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.post("/prime")
async def prime_cache(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Prime the cache with test data for each layer.
    Simulates cache entries that would be created during normal operation.
    """
    # Generate a unique ID for this test run
    test_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # HTTP cache layer test data
    http_cache_key = f"http:{test_id}"
    http_cache_value = json.dumps({
        "status": "success",
        "data": {
            "message": "Test HTTP cache entry",
            "timestamp": timestamp,
            "test_id": test_id
        }
    })
    
    # Service layer test data
    service_cache_key = f"lead:get_lead:{test_id}"
    service_cache_value = json.dumps({
        "id": test_id,
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "timestamp": timestamp
    })
    
    # Repository layer test data
    repo_cache_key = f"lead_query:get_lead_by_id:{test_id}"
    repo_cache_value = json.dumps({
        "id": test_id,
        "data": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "timestamp": timestamp
        }
    })
    
    try:
        # Get Redis client
        redis_client = get_redis_client()
        
        if not redis_client:
            raise HTTPException(
                status_code=503,
                detail="Redis client not initialized"
            )
        
        # Store test data in cache with 5 minute TTL
        await redis_client.setex(http_cache_key, 300, http_cache_value)
        await redis_client.setex(service_cache_key, 300, service_cache_value)
        await redis_client.setex(repo_cache_key, 300, repo_cache_value)
        
        return {
            "success": True,
            "message": "Cache successfully primed with test data",
            "test_id": test_id,
            "keys": [http_cache_key, service_cache_key, repo_cache_key],
            "ttl": 300  # 5 minutes
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to prime cache: {str(e)}"
        )

@router.post("/clear")
async def clear_cache(
    pattern: str = "test:*",
    current_user: User = Depends(get_current_user)
):
    """
    Clear cache entries matching a pattern.
    Default pattern is "test:*" to only clear test data.
    
    WARNING: Use with caution! Pattern "*" will clear ALL cache data.
    
    Args:
        pattern: Redis key pattern to match (default: "test:*")
    """
    try:
        # Get Redis client
        redis_client = get_redis_client()
        
        if not redis_client:
            raise HTTPException(
                status_code=503,
                detail="Redis client not initialized"
            )
        
        # Find keys matching the pattern
        keys = await redis_client.keys(pattern)
        
        if not keys:
            return {
                "success": True,
                "message": "No keys found matching the pattern",
                "pattern": pattern,
                "count": 0
            }
        
        # Delete all matching keys
        deleted = await redis_client.delete(*keys)
        
        return {
            "success": True,
            "message": f"Successfully cleared {deleted} cache entries",
            "pattern": pattern,
            "count": deleted
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        ) 