from fastapi import APIRouter
from app.routes.knowledge import entries, sources, import_routes

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

# Include subrouters
router.include_router(entries.router)
router.include_router(sources.router)
router.include_router(import_routes.router) 