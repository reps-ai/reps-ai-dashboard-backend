from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, leads, calls, appointments, analytics, settings, agent, voice_agent, knowledge

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
app.include_router(appointments.router, tags=["Appointment Management"])
app.include_router(analytics.router, tags=["Analytics"])
app.include_router(settings.router, tags=["Settings"])
app.include_router(agent.router, tags=["AI Voice Agent"])
app.include_router(voice_agent.router, tags=["Voice Agent"])
app.include_router(knowledge.router, tags=["Knowledge Base"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Gym AI Voice Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 