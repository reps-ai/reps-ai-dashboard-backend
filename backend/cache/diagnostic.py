"""
Cache diagnostic utilities for testing and debugging cache functionality.
"""

import json
import redis.asyncio as redis
import time
import logging
import traceback
import sys
from typing import Dict, Any, List, Optional
from pprint import pformat

from . import get_redis_client

# Set up a dedicated logger for cache diagnostics
logger = logging.getLogger("cache_diagnostics")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

async def test_redis_connection() -> Dict[str, Any]:
    """
    Test if Redis connection is working.
    
    Returns:
        Dict with test results
    """
    logger.info("Testing Redis connection...")
    result = {
        "success": False,
        "errors": [],
        "details": {}
    }
    
    try:
        # Get the Redis client
        redis_client = get_redis_client()
        
        if not redis_client:
            raise Exception("Redis client is not initialized")
            
        # Test connection with ping
        ping_start = time.time()
        pong = await redis_client.ping()
        ping_time = time.time() - ping_start
        
        result["details"]["ping"] = {
            "response": pong,
            "time_ms": ping_time * 1000
        }
        
        # Test setting a key
        set_start = time.time()
        test_key = "diagnostic:test:connection"
        test_value = json.dumps({
            "timestamp": time.time(),
            "test": "connection"
        })
        
        await redis_client.setex(test_key, 60, test_value)
        set_time = time.time() - set_start
        
        # Test getting the key
        get_start = time.time()
        retrieved = await redis_client.get(test_key)
        get_time = time.time() - get_start
        
        # Clean up
        await redis_client.delete(test_key)
        
        result["details"]["set"] = {
            "success": True,
            "time_ms": set_time * 1000
        }
        
        result["details"]["get"] = {
            "success": retrieved is not None,
            "time_ms": get_time * 1000,
            "value_match": retrieved.decode() == test_value if retrieved else False
        }
        
        result["success"] = True
        logger.info("Redis connection test successful!")
        
    except Exception as e:
        error_details = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        result["errors"].append(error_details)
        logger.error(f"Redis connection test failed: {str(e)}")
        logger.debug(traceback.format_exc())
    
    return result

async def inspect_cache_keys(pattern: str = "*") -> Dict[str, Any]:
    """
    Inspect keys in Redis matching a pattern.
    
    Args:
        pattern: Redis key pattern to match
        
    Returns:
        Dict with inspection results
    """
    logger.info(f"Inspecting Redis keys matching pattern: {pattern}")
    result = {
        "success": False,
        "errors": [],
        "keys_count": 0,
        "keys": [],
        "details": {}
    }
    
    try:
        # Get the Redis client
        redis_client = get_redis_client()
        
        if not redis_client:
            raise Exception("Redis client is not initialized")
            
        # Get all keys matching the pattern
        keys = await redis_client.keys(pattern)
        result["keys_count"] = len(keys)
        
        # Get details for each key (up to 20 keys to avoid overwhelming logs)
        for i, key in enumerate(keys[:20]):
            key_str = key.decode()
            result["keys"].append(key_str)
            
            # Get type of the key
            key_type = await redis_client.type(key)
            
            # Get TTL
            ttl = await redis_client.ttl(key)
            
            # Get value preview (truncated for large values)
            value_preview = None
            if key_type.decode() == "string":
                value = await redis_client.get(key)
                if value:
                    try:
                        # Try to decode and parse as JSON
                        value_str = value.decode()
                        if len(value_str) > 200:
                            value_preview = value_str[:200] + "... (truncated)"
                        else:
                            value_preview = value_str
                            
                            # Try to parse as JSON for better formatting
                            try:
                                json_value = json.loads(value_str)
                                value_preview = f"JSON: {type(json_value).__name__} with keys: {list(json_value.keys()) if isinstance(json_value, dict) else 'N/A'}"
                            except json.JSONDecodeError:
                                pass
                    except UnicodeDecodeError:
                        value_preview = f"Binary data, size: {len(value)} bytes"
            
            result["details"][key_str] = {
                "type": key_type.decode(),
                "ttl": ttl,
                "value_preview": value_preview
            }
        
        if len(keys) > 20:
            result["truncated"] = True
            result["total_keys"] = len(keys)
        
        result["success"] = True
        logger.info(f"Found {len(keys)} keys matching pattern: {pattern}")
        
    except Exception as e:
        error_details = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        result["errors"].append(error_details)
        logger.error(f"Cache inspection failed: {str(e)}")
        logger.debug(traceback.format_exc())
    
    return result

async def test_cache_layers() -> Dict[str, Any]:
    """
    Test all cache layers with sample data.
    
    Returns:
        Dict with test results for each layer
    """
    logger.info("Testing all cache layers...")
    result = {
        "success": False,
        "errors": [],
        "layers": {}
    }
    
    try:
        # Get the Redis client
        redis_client = get_redis_client()
        
        if not redis_client:
            raise Exception("Redis client is not initialized")
        
        # Test HTTP layer (simple key simulation)
        http_result = await test_cache_layer(
            "http", 
            "http:test:endpoint", 
            json.dumps({"status": "success", "data": {"test": True}}),
            300
        )
        result["layers"]["http"] = http_result
        
        # Test service layer
        service_result = await test_cache_layer(
            "service",
            "lead:get_lead:test-id",
            json.dumps({"id": "test-id", "name": "Test Lead", "email": "test@example.com"}),
            300
        )
        result["layers"]["service"] = service_result
        
        # Test repository layer
        repo_result = await test_cache_layer(
            "repository",
            "lead_query:get_lead_by_id:test-id",
            json.dumps({"id": "test-id", "data": {"name": "Test Lead"}}),
            300
        )
        result["layers"]["repository"] = repo_result
        
        # Overall success is based on all tests succeeding
        result["success"] = all(
            layer["success"] for layer in result["layers"].values()
        )
        
        logger.info(f"Cache layer tests completed: {result['success']}")
        
    except Exception as e:
        error_details = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        result["errors"].append(error_details)
        logger.error(f"Cache layer tests failed: {str(e)}")
        logger.debug(traceback.format_exc())
    
    return result

async def test_cache_layer(layer_name: str, key: str, value: str, ttl: int) -> Dict[str, Any]:
    """
    Test a specific cache layer with a test key.
    
    Args:
        layer_name: Name of the cache layer
        key: Test key to use
        value: Test value to store
        ttl: TTL in seconds
        
    Returns:
        Dict with test results
    """
    logger.info(f"Testing {layer_name} cache layer with key: {key}")
    result = {
        "success": False,
        "errors": [],
        "operations": {}
    }
    
    try:
        # Get the Redis client
        redis_client = get_redis_client()
        
        if not redis_client:
            raise Exception(f"Redis client is not initialized for {layer_name} layer test")
            
        # Set the test key
        set_start = time.time()
        await redis_client.setex(key, ttl, value)
        set_time = time.time() - set_start
        
        result["operations"]["set"] = {
            "success": True,
            "time_ms": set_time * 1000
        }
        
        # Get the test key
        get_start = time.time()
        retrieved = await redis_client.get(key)
        get_time = time.time() - get_start
        
        if retrieved:
            decoded = retrieved.decode()
            value_match = decoded == value
        else:
            decoded = None
            value_match = False
        
        result["operations"]["get"] = {
            "success": retrieved is not None,
            "time_ms": get_time * 1000,
            "value_match": value_match
        }
        
        # Check TTL
        ttl_value = await redis_client.ttl(key)
        
        result["operations"]["ttl"] = {
            "success": ttl_value > 0,
            "value": ttl_value
        }
        
        # Delete the test key
        delete_start = time.time()
        deleted = await redis_client.delete(key)
        delete_time = time.time() - delete_start
        
        result["operations"]["delete"] = {
            "success": deleted > 0,
            "time_ms": delete_time * 1000
        }
        
        # Final verification
        exists = await redis_client.exists(key)
        
        result["operations"]["verify_deleted"] = {
            "success": exists == 0
        }
        
        # Overall success
        result["success"] = all(
            op["success"] for op in result["operations"].values()
        )
        
        logger.info(f"{layer_name} cache layer test {'succeeded' if result['success'] else 'failed'}")
        
    except Exception as e:
        error_details = {
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        result["errors"].append(error_details)
        logger.error(f"{layer_name} cache layer test failed: {str(e)}")
        logger.debug(traceback.format_exc())
    
    return result

async def run_all_diagnostic_tests() -> Dict[str, Any]:
    """
    Run all diagnostic tests and return comprehensive results.
    
    Returns:
        Dict with all test results
    """
    logger.info("Starting comprehensive cache diagnostics...")
    
    results = {
        "timestamp": time.time(),
        "tests": {}
    }
    
    # Test basic Redis connection
    results["tests"]["connection"] = await test_redis_connection()
    
    # Skip other tests if connection fails
    if not results["tests"]["connection"]["success"]:
        logger.error("Connection test failed, skipping remaining tests")
        return results
    
    # Test all cache layers
    results["tests"]["layers"] = await test_cache_layers()
    
    # Inspect existing keys for each layer
    results["tests"]["inspection"] = {
        "all": await inspect_cache_keys("*"),
        "http": await inspect_cache_keys("http:*"),
        "service": await inspect_cache_keys("lead:*"),
        "repository": await inspect_cache_keys("lead_query:*")
    }
    
    logger.info("Cache diagnostics completed")
    return results 