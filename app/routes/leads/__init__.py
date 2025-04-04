from fastapi import APIRouter
from app.routes.leads import entries, status, import_routes

router = APIRouter(prefix="/api/leads", tags=["Lead Management"])

# Include subrouters
router.include_router(entries.router)
router.include_router(status.router)
router.include_router(import_routes.router) 