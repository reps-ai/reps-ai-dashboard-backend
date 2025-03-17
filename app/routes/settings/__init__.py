from fastapi import APIRouter
from app.routes.settings import gym, voice, ai, call, knowledge, notifications, integrations

router = APIRouter(prefix="/api/settings", tags=["Settings"])

# Include subrouters
router.include_router(gym.router)
router.include_router(voice.router)
router.include_router(ai.router)
router.include_router(call.router)
router.include_router(knowledge.router)
router.include_router(notifications.router)
router.include_router(integrations.router) 