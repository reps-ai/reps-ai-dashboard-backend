from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.db.connections.database import check_db_connection
from backend.cache import setup_redis
from backend.cache.http_cache import HttpResponseCacheMiddleware
import os

from app.routes import auth, leads, calls

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

# Add HTTP response caching middleware
app.add_middleware(
    HttpResponseCacheMiddleware,
    cacheable_paths={
        "/api/leads": 300,                # 5 minutes for lead lists
        "/api/leads/prioritized": 600,    # 10 minutes for prioritized leads
        "/api/leads/branch/": 300,        # 5 minutes for branch leads
        "/health": 1800,                  # 30 minutes for health check
    },
    enable_cache_header=True
)

app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(calls.router)


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
    try:
        redis_client = setup_redis(REDIS_URL)
        print(f"Redis client initialized with URL: {REDIS_URL}")
    except Exception as e:
        print(f"Warning: Redis client initialization failed: {str(e)}")
        print("Caching will be disabled")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)