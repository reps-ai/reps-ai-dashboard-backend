from fastapi import APIRouter
from app.routes.agent import scripts, prompts, responses

router = APIRouter(prefix="/api/agent", tags=["AI Voice Agent"])

# Include subrouters
router.include_router(scripts.router)
router.include_router(prompts.router)
router.include_router(responses.router) 