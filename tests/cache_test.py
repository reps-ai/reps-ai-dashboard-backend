"""
Simple test script to verify Redis caching functionality.
"""

import asyncio
import sys
import time
import json
import uuid
from datetime import datetime

sys.path.append(".")  # Add the current directory to the path

import redis.asyncio as redis

# Connect to Redis
redis_url = "redis://localhost:6379/0"
redis_client = redis.Redis.from_url(redis_url)

async def test_redis_connection():
    """Test basic Redis connection and operations."""
    print("Testing Redis connection...")
    
    try:
        # Test connection
        await redis_client.ping()
        print("✅ Redis connection successful!")
        
        # Test basic operations
        test_key = f"test:cache:{datetime.now().isoformat()}"
        test_data = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "test": True
        }
        
        # Set data
        await redis_client.setex(test_key, 60, json.dumps(test_data))
        print(f"✅ Set test data with key: {test_key}")
        
        # Get data
        retrieved = await redis_client.get(test_key)
        retrieved_data = json.loads(retrieved)
        print(f"✅ Retrieved test data: {retrieved_data}")
        
        # Test TTL
        ttl = await redis_client.ttl(test_key)
        print(f"✅ TTL for test key: {ttl} seconds")
        
        # Test delete
        await redis_client.delete(test_key)
        print(f"✅ Deleted test key")
        
        # Verify deletion
        exists = await redis_client.exists(test_key)
        if not exists:
            print(f"✅ Verified key deletion")
        else:
            print(f"❌ Key still exists after deletion")
            
        return True
        
    except Exception as e:
        print(f"❌ Redis test failed: {str(e)}")
        return False

async def test_cache_performance():
    """Test cache performance with simulated operations."""
    print("\nTesting cache performance...")
    
    # Generate test data
    test_data = {
        "id": str(uuid.uuid4()),
        "name": "Test Lead",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "created_at": datetime.now().isoformat(),
        "tags": ["test", "cache", "performance"],
        "notes": "This is a test lead for cache performance testing.",
        "large_field": "x" * 1000  # Add some size to the data
    }
    
    # Convert to JSON
    test_json = json.dumps(test_data)
    
    # Test keys
    uncached_key = f"test:uncached:{uuid.uuid4()}"
    cached_key = f"test:cached:{uuid.uuid4()}"
    
    # Set the cached key in advance
    await redis_client.setex(cached_key, 3600, test_json)
    
    # Test uncached performance
    print("Testing uncached performance (simulating database operation)...")
    uncached_start = time.time()
    
    # Simulate database operation by sleeping
    await asyncio.sleep(0.1)  # 100ms database operation simulation
    
    # Set the value after "database" operation
    await redis_client.setex(uncached_key, 3600, test_json)
    
    uncached_duration = time.time() - uncached_start
    print(f"✅ Uncached operation completed in {uncached_duration:.6f} seconds")
    
    # Test cached performance
    print("Testing cached performance...")
    cached_start = time.time()
    
    # Get from cache
    cached_result = await redis_client.get(cached_key)
    
    cached_duration = time.time() - cached_start
    print(f"✅ Cached operation completed in {cached_duration:.6f} seconds")
    
    # Calculate speedup
    speedup = uncached_duration / cached_duration
    print(f"🚀 Cache speedup: {speedup:.2f}x faster")
    
    # Clean up
    await redis_client.delete(uncached_key, cached_key)
    
    return True

async def test_pattern_deletion():
    """Test pattern-based cache invalidation."""
    print("\nTesting pattern-based cache invalidation...")
    
    # Create several test keys with a common pattern
    test_id = str(uuid.uuid4())
    
    for i in range(10):
        key = f"test:lead:{test_id}:attribute:{i}"
        await redis_client.setex(key, 3600, f"value-{i}")
        
    # Count keys matching the pattern
    keys = await redis_client.keys(f"test:lead:{test_id}:*")
    print(f"✅ Created {len(keys)} test keys")
    
    # Delete keys by pattern
    pattern = f"test:lead:{test_id}:*"
    deleted_count = 0
    
    for key in keys:
        await redis_client.delete(key)
        deleted_count += 1
        
    print(f"✅ Deleted {deleted_count} keys matching pattern: {pattern}")
    
    # Verify deletion
    remaining = await redis_client.keys(pattern)
    if not remaining:
        print(f"✅ Successfully deleted all keys matching the pattern")
    else:
        print(f"❌ Still have {len(remaining)} keys remaining")
        
    return True

async def main():
    """Run all cache tests."""
    print("===== Redis Cache Test =====")
    print(f"Redis URL: {redis_url}")
    print("===========================")
    
    # Run connection test
    connection_ok = await test_redis_connection()
    if not connection_ok:
        print("❌ Basic Redis connection test failed. Exiting.")
        return
    
    # Run performance test
    await test_cache_performance()
    
    # Run pattern deletion test
    await test_pattern_deletion()
    
    print("\n✅ All tests completed!")
    
    # Clean up connection
    await redis_client.close()

if __name__ == "__main__":
    asyncio.run(main()) 