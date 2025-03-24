from fastapi import APIRouter, Depends, Path, Body
from app.dependencies import get_current_user

from app.schemas.appointments.base import AppointmentStatusUpdate
from app.schemas.appointments.responses import AppointmentStatusResponse

router = APIRouter()

@router.patch("/{id}/status", response_model=AppointmentStatusResponse)
async def update_appointment_status(
    id: str = Path(..., description="The ID of the appointment to update status for"),
    status_update: AppointmentStatusUpdate = Body(...),
    current_user = Depends(get_current_user)
):
    """
    Update the status of an appointment (confirm/cancel).
    """
    # Implementation will be added later
    pass 