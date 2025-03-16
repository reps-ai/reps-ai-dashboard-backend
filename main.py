from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, leads, calls, analytics, settings, agent

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
app.include_router(analytics.router, tags=["Analytics"])
app.include_router(settings.router, tags=["Settings"])
app.include_router(agent.router, tags=["AI Voice Agent"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Gym AI Voice Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 