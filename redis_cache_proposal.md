# Redis Cache Implementation for API Performance

## Overview

Based on our stress testing results, we've identified performance bottlenecks in the leads API endpoints. Implementing a multi-level caching strategy with Redis will reduce database load and improve response times across the application stack.

## Problem Statement

Our stress testing reveals:
- API achieves ~87 RPS at 500 concurrent users with 99.9% success rate
- Performance degrades at 1000+ concurrent users (98.5% success rate)
- Significant timeouts occur at 2000+ concurrent users (95% success rate)

Database queries are likely the primary bottleneck, particularly for frequently accessed and rarely changing data.

## Proposed Multi-Level Caching Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │     │             │
│  Client     │────▶│  HTTP Cache │────▶│  FastAPI    │────▶│  Service    │────▶│  Database   │
│  Request    │◀────│  Layer      │◀────│  Backend    │◀────│  Layer      │◀────│  Layer      │
│             │     │             │     │             │     │  Cache      │     │  Cache      │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                 │                    │
                                                                 ▼                    ▼
                                                            ┌─────────────┐     ┌─────────────┐
                                                            │             │     │             │
                                                            │  Redis      │     │  Postgres   │
                                                            │  Cache      │     │  Database   │
                                                            │             │     │             │
                                                            └─────────────┘     └─────────────┘
```

### Cache Levels

1. **HTTP Cache Layer**
   - Client-side and CDN caching with appropriate Cache-Control headers
   - Helps reduce requests to the backend entirely
   - Most effective for static or semi-static data (e.g., lead categories, static configs)
   - Cache duration: 5-60 minutes depending on data volatility
   - Implementation: HTTP headers, ETag, Conditional GET support

2. **Service Layer Cache (API Response Cache)**
   - Redis-based caching of fully formed API responses
   - Sits between API controllers and data services
   - Caches final, serialized results of common API calls
   - Cache duration: 1-10 minutes for dynamic data
   - Implementation: Decorators on FastAPI route handlers

3. **Database Layer Cache (Query Results Cache)**
   - Redis-based caching of database query results
   - Sits between service and database layers
   - Caches raw data, query results, and computed values
   - Cache duration: 30 seconds to 5 minutes
   - Implementation: Interceptors for database operations

### Components

1. **Redis Cache Server**
   - Standalone instance or managed service (AWS ElastiCache, etc.)
   - In-memory data store for fast access
   - Key namespacing to separate different cache levels
   - Configurable TTL (Time-To-Live) for different data types

2. **Cache Layer Integration**
   - HTTP headers and cache controls for browser/CDN caching
   - Middleware approach for transparent API response caching
   - Decorator pattern for selective endpoint caching
   - Data access interceptors for database query caching
   - Custom cache utilities for manual cache management

3. **Cache Invalidation Strategy**
   - Time-based expiration for most data (configurable TTL)
   - Event-based invalidation for modified data
   - Hierarchical invalidation (e.g., invalidating related entities)
   - Bulk invalidation capabilities for admin operations

## Implementation Plan

### Phase 1: Infrastructure Setup

- Deploy Redis server instance
- Configure security groups and network access
- Set up monitoring and alerting
- Implement connection pooling
- Define cache key namespaces for different cache levels

### Phase 2: Core Implementation

- Develop cache utility functions:
  ```python
  async def get_cache(key: str, namespace: str = "default") -> Optional[dict]:
      """Get data from cache"""
  
  async def set_cache(key: str, data: dict, ttl: int = 3600, namespace: str = "default") -> bool:
      """Set data in cache with TTL"""
  
  async def invalidate_cache(key: str, namespace: str = "default") -> bool:
      """Remove specific key from cache"""
      
  async def invalidate_pattern(pattern: str, namespace: str = "default") -> int:
      """Remove multiple keys matching a pattern"""
  ```

- Implement HTTP cache headers:
  ```python
  @app.get("/leads/categories/")
  async def get_lead_categories():
      response = JSONResponse(...)
      response.headers["Cache-Control"] = "public, max-age=3600"
      response.headers["ETag"] = generate_etag(...)
      return response
  ```

- Implement API response caching decorator:
  ```python
  def cache_response(ttl: int = 3600, key_prefix: str = "", namespace: str = "api"):
      """Decorator to cache API responses"""
      def decorator(func):
          @wraps(func)
          async def wrapper(*args, **kwargs):
              # Generate cache key from function args and request details
              # Check cache before executing function
              # Return cached result or execute function and cache
          return wrapper
      return decorator
  ```
  
- Implement database query cache:
  ```python
  async def cached_query(query_func, key: str, ttl: int = 300, namespace: str = "db"):
      """Executes a database query with caching"""
      cache_key = f"{namespace}:{key}"
      cached_result = await get_cache(cache_key)
      if cached_result:
          return cached_result
      
      result = await query_func()
      await set_cache(cache_key, result, ttl, namespace)
      return result
  ```

### Phase 3: Integration with Endpoints

- Prioritize high-traffic endpoints:
  - **HTTP Cache Level**:
    - `/api/static/config` - 1 hour cache via HTTP headers
    - `/api/leads/categories` - 30 minute cache via HTTP headers
  
  - **API Response Cache Level**:
    - `/api/leads/` (GET all leads) - 5 minute cache
    - `/api/leads/{id}/` (GET single lead) - 10 minute cache
    - `/api/leads/summary` (GET leads statistics) - 15 minute cache
  
  - **DB Query Cache Level**:
    - Lead lookup by ID - 5 minute cache
    - Lead count queries - 2 minute cache
    - User authorization data - 1 minute cache

- Implement cache invalidation:
  - Integrate with model update events
  - Clear relevant caches across all levels on data modification
  - Implement cascade invalidation for related entities

### Phase 4: Optimizations

- Implement cache warming for frequently accessed data
- Add compression for large payloads
- Investigate batch operations for multiple keys
- Consider partitioned cache keys based on user context
- Implement cache stampede protection for high-traffic keys

## Expected Performance Improvements

- HTTP Cache: Reduce server requests by 30-40% for cacheable endpoints
- API Response Cache: Reduce service layer processing by 60-70%
- DB Query Cache: Reduce database load by 70-80% for read operations
- Overall response time improvement: 100-300ms (depending on query complexity)
- Support 2000+ concurrent users with 99%+ success rate
- Scale to 150+ RPS without timeout issues

## Monitoring & Maintenance

- Cache hit/miss ratio monitoring for each cache level
- Memory usage tracking with alerts
- Automated cache pruning for size management
- Regular performance benchmarking
- Heat maps for most frequently accessed cache keys

## Future Considerations

- Potential for distributed Redis cluster for higher scale
- Explore Redis Pub/Sub for real-time cache invalidation
- Evaluate read-through/write-through cache patterns
- Consider Redis Streams for event processing
- Investigate edge caching via CDN for global performance

## Next Steps

- [ ] Set up Redis instance with namespace configuration
- [ ] Implement HTTP cache headers for static resources
- [ ] Develop service layer caching for API responses
- [ ] Build database query caching utilities
- [ ] Integrate with highest traffic endpoints
- [ ] Benchmark performance improvements for each cache layer
- [ ] Roll out to all suitable endpoints
- [ ] Document cache management procedures

## References

- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Caching Best Practices](https://fastapi.tiangolo.com/)
- [HTTP Caching - MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
- [Our stress test results and metrics](https://github.com/your-org/your-repo/pull/123) 