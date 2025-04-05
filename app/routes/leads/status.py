from fastapi import APIRouter, Path, Body, Depends, HTTPException, status
from app.schemas.leads.base import LeadStatusUpdate
from app.schemas.leads.responses import LeadResponse
from app.dependencies import get_current_user, get_current_gym, get_lead_service
from backend.services.lead.implementation import DefaultLeadService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.patch("/{id}/status", response_model=LeadResponse)
async def update_lead_status(
    id: str = Path(..., description="The ID of the lead to update"),
    status_update: LeadStatusUpdate = Body(...),
    current_gym: dict = Depends(get_current_gym),
    lead_service: DefaultLeadService = Depends(get_lead_service)
):
    """
    Update the status of a lead.
    Only updates the lead if it belongs to the current user's gym.
    """
    try:
        # First check if lead exists and belongs to this gym
        existing_lead = await lead_service.get_lead(id)
        
        if str(existing_lead.get("gym_id")) != str(current_gym.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found or does not belong to your gym"
            )
        
        # Update the lead status
        lead_data = {"status": status_update.status}
        updated_lead = await lead_service.update_lead(id, lead_data)
        
        # Format the lead response using the same formatter from entries.py
        from app.routes.leads.entries import format_lead_for_response
        formatted_lead = format_lead_for_response(updated_lead)
        return formatted_lead
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating lead status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )