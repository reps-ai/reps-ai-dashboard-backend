from fastapi import APIRouter
from app.routes.appointments import entries, status, availability

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

# Include subrouters
router.include_router(entries.router)
router.include_router(status.router)
router.include_router(availability.router) 