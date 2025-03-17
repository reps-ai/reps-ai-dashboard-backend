from fastapi import APIRouter, Depends, Query
from app.dependencies import get_current_user

from app.schemas.appointments.responses import AvailabilityResponse

router = APIRouter()

@router.get("/availability", response_model=AvailabilityResponse)
async def get_availability(
    branch_id: str = Query(..., description="The ID of the branch to check availability for"),
    date: str = Query(..., description="The date to check availability for (YYYY-MM-DD)"),
    duration: int = Query(60, description="The duration of the appointment in minutes"),
    current_user = Depends(get_current_user)
):
    """
    Get available time slots for a specific branch and date.
    """
    # Implementation will be added later
    pass 