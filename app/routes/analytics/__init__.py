from fastapi import APIRouter
from app.routes.analytics import metrics

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# Include subrouters
router.include_router(metrics.router)
