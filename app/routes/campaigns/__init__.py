"""
Campaign routes module.
"""
from fastapi import APIRouter
from .entries import router as entries_router
from .schedule import router as schedule_router

router = APIRouter(prefix="/api/campaigns", tags=["Campaign Management"])

# Include subrouters
router.include_router(entries_router)
router.include_router(schedule_router)
