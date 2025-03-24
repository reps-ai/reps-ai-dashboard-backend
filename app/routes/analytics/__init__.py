from fastapi import APIRouter
from app.routes.analytics import overview, leads, calls, sentiment, funnel, performance

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# Include subrouters
router.include_router(overview.router)
router.include_router(leads.router)
router.include_router(calls.router)
router.include_router(sentiment.router)
router.include_router(funnel.router)
router.include_router(performance.router) 