from fastapi import APIRouter
from app.routes.voice_agent import calls, webhooks, recordings

router = APIRouter(prefix="/api/voice-agent", tags=["Voice Agent"])

# Include subrouters
router.include_router(calls.router)
router.include_router(webhooks.router)
router.include_router(recordings.router) 