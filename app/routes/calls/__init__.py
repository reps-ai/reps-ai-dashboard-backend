from fastapi import APIRouter
from app.routes.calls import entries, details, campaign, webhooks

router = APIRouter(prefix="/api/calls", tags=["calls"])

# Include subrouters
router.include_router(entries.router)
router.include_router(details.router)
router.include_router(campaign.router) 
router.include_router(webhooks.router) 