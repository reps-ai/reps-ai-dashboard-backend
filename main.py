from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.db.connections.database import check_db_connection
from backend.cache import setup_redis, get_redis_client
from backend.cache.http_cache import HttpResponseCacheMiddleware
import os
import logging
import asyncio
from fastapi_mcp import FastApiMCP

from app.routes import auth, leads, calls, cache_diagnostics

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("main")

# Get Redis URL from environment variable or use default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = FastAPI(
    title="Gym AI Voice Agent API",
    description="API for AI Voice Agent system for gyms",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the cacheable paths
cacheable_paths = {
    "/api/leads": 300,                # 5 minutes for lead lists
    "/api/leads/prioritized": 600,    # 10 minutes for prioritized leads
    "/api/leads/branch/": 300,        # 5 minutes for branch leads
    "/health": 1800,                  # 30 minutes for health check
}

# Add the middleware to the app - only need to do this once
app.add_middleware(
    HttpResponseCacheMiddleware,
    cacheable_paths=cacheable_paths,
    enable_cache_header=True
)

# Get a reference to the actual middleware instance
# FastAPI middleware stack has the middleware instances in reverse order
# So the last one added is at index 0
if app.middleware_stack and hasattr(app.middleware_stack.middlewares, "__getitem__"):
    http_cache_middleware = app.middleware_stack.middlewares[0]
    # Store middleware in app.state for diagnostics
    app.state.http_cache_middleware = http_cache_middleware
    logger.info("HTTP cache middleware stored in app.state")
else:
    logger.warning("Could not get reference to HTTP cache middleware")

app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(calls.router)
app.include_router(cache_diagnostics.router)  # Add cache diagnostics routes


@app.get("/")
async def root():
    return {"message": "Welcome to the Gym AI Voice Agent API"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API and database connectivity
    """
    db_connected = await check_db_connection()
    
    if not db_connected:
        raise HTTPException(
            status_code=503,
            detail="Database connection error"
        )
    
    return {
        "status": "healthy",
        "database": "connected"
    }

@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    Initialize services like Redis.
    """
    # Initialize Redis client
    redis_client = setup_redis(REDIS_URL)
    if redis_client is None:
        logger.warning("Redis client initialization returned None, caching disabled for this session")
        return
    try:
        # Verify the Redis connection is working with a simple ping
        loop = asyncio.get_event_loop()
        ping_result = await asyncio.wait_for(redis_client.ping(), timeout=2.0)
        
        if ping_result:
            logger.info(f"Redis connection verified - ping successful")
            
            # Set a test key to verify write operations
            await redis_client.setex("startup:test", 30, "Application startup test")
            logger.info(f"Redis write operation successful")
            
            # Manually verify that the get_redis_client function returns the correct client
            test_client = get_redis_client()
            if test_client:
                logger.info("get_redis_client() is working correctly")
            else:
                logger.error("get_redis_client() returned None even though Redis was initialized")
        else:
            logger.error("Redis ping failed")
            raise Exception("Redis ping failed")
    except Exception as e:
        logger.error(f"Redis client initialization failed: {str(e)}")
        logger.warning("Caching will be disabled")
        
        # Explicitly attempt to recover by calling get_redis_client later
        logger.info("Redis client will be re-attempted when needed via get_redis_client()")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)