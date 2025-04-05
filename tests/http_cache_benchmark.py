"""
Benchmark script to test HTTP caching performance.
"""

import asyncio
import sys
import time
import json
import statistics
from datetime import datetime

import httpx

# Base URL for the API
BASE_URL = "http://localhost:8000"

async def benchmark_endpoint(endpoint: str, iterations: int = 5, warmup: int = 1):
    """
    Benchmark a specific API endpoint.
    
    Args:
        endpoint: The API endpoint to test (e.g., "/api/leads")
        iterations: Number of requests to make
        warmup: Number of warmup requests
        
    Returns:
        Dict with benchmark results
    """
    url = f"{BASE_URL}{endpoint}"
    print(f"Benchmarking {url}...")
    
    # Create an HTTP client
    async with httpx.AsyncClient() as client:
        # Warm up requests to initialize any internal caches
        print(f"Performing {warmup} warm-up requests...")
        for _ in range(warmup):
            await client.get(url)
            
        # First uncached request (should miss cache)
        print("Testing first request (cache miss)...")
        start_time = time.time()
        response = await client.get(url)
        first_request_time = time.time() - start_time
        
        # Check if we got a valid response
        if response.status_code != 200:
            print(f"❌ Error: Received status code {response.status_code}")
            return {
                "endpoint": endpoint,
                "error": f"HTTP {response.status_code}",
                "response": response.text
            }
            
        # Check for cache headers
        cache_status = response.headers.get("X-Cache", "UNKNOWN")
        print(f"First request complete in {first_request_time:.6f}s, cache status: {cache_status}")
        
        # Subsequent requests (should hit cache if caching is enabled)
        print(f"Performing {iterations} cached requests...")
        cached_times = []
        
        for i in range(iterations):
            start_time = time.time()
            response = await client.get(url)
            request_time = time.time() - start_time
            cached_times.append(request_time)
            
            cache_status = response.headers.get("X-Cache", "UNKNOWN")
            print(f"Request {i+1}/{iterations} complete in {request_time:.6f}s, cache status: {cache_status}")
        
        # Calculate statistics
        avg_cached_time = statistics.mean(cached_times)
        min_cached_time = min(cached_times)
        max_cached_time = max(cached_times)
        
        # Calculate speedup
        if first_request_time > 0:
            speedup = first_request_time / avg_cached_time
        else:
            speedup = 0
            
        print(f"\nResults for {endpoint}:")
        print(f"First request (cache miss): {first_request_time:.6f}s")
        print(f"Average cached request: {avg_cached_time:.6f}s")
        print(f"Min cached request: {min_cached_time:.6f}s")
        print(f"Max cached request: {max_cached_time:.6f}s")
        print(f"Speedup: {speedup:.2f}x")
        
        return {
            "endpoint": endpoint,
            "first_request_time": first_request_time,
            "avg_cached_time": avg_cached_time,
            "min_cached_time": min_cached_time,
            "max_cached_time": max_cached_time,
            "cached_times": cached_times,
            "speedup": speedup
        }

async def main():
    """Run HTTP cache benchmarks on several endpoints."""
    print("===== HTTP Cache Benchmark =====")
    print(f"Base URL: {BASE_URL}")
    print("===============================")
    
    # List of endpoints to test
    endpoints = [
        "/health",                         # Should be cached for 300s
        "/api/leads?page=1&limit=10",      # Should be cached for 30s
        # Add more endpoints as needed
    ]
    
    results = {}
    
    # Run benchmarks
    for endpoint in endpoints:
        try:
            result = await benchmark_endpoint(endpoint, iterations=5, warmup=1)
            results[endpoint] = result
            print("-" * 40)
        except Exception as e:
            print(f"❌ Error benchmarking {endpoint}: {str(e)}")
            results[endpoint] = {"error": str(e)}
    
    # Print summary
    print("\n===== Benchmark Summary =====")
    for endpoint, result in results.items():
        if "error" in result:
            print(f"{endpoint}: ERROR - {result['error']}")
        else:
            print(f"{endpoint}: {result['speedup']:.2f}x speedup " +
                  f"({result['first_request_time']:.6f}s → {result['avg_cached_time']:.6f}s)")
    
    print("\n✅ All benchmarks completed!")

if __name__ == "__main__":
    asyncio.run(main()) 