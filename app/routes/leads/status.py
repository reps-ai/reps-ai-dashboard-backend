from fastapi import APIRouter, Path, Body
from app.schemas.leads.base import LeadStatusUpdate
from app.schemas.leads.responses import LeadResponse

router = APIRouter()

@router.patch("/{id}/status", response_model=LeadResponse)
async def update_lead_status(
    id: str = Path(..., description="The ID of the lead to update"),
    status_update: LeadStatusUpdate = Body(...)
):
    """
    Update the status of a lead.
    """
    # Implementation will be added later
    pass 