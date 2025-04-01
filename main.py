from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.db.connections.database import check_db_connection

from app.routes import auth, leads, calls

app = FastAPI(
    title="Gym AI Voice Agent API",
    description="API for AI Voice Agent system for gyms",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(leads.router, tags=["Lead Management"])
app.include_router(calls.router, tags=["Call Management"])


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)