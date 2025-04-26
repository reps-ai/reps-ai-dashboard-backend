"""
Campaign scheduling routes.
"""
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, status
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid
import logging

from app.schemas.campaigns.base import CampaignSchedule
from app.schemas.campaigns.responses import CampaignScheduleResponse
from app.dependencies import get_current_user, get_current_gym, get_current_branch, User, Gym, Branch, get_campaign_service
from backend.services.campaign.implementation import DefaultCampaignService

# Create router without prefix
router = APIRouter()
logger = logging.getLogger(__name__)

# Define routes directly on this router
@router.post("/{campaign_id}/schedule", response_model=CampaignScheduleResponse)
async def schedule_campaign_calls(
    campaign_id: str = Path(..., description="The ID of the campaign to schedule calls for"),
    target_date: Optional[date] = Query(None, description="The date to schedule calls for (defaults to today)"),
    current_branch: Branch = Depends(get_current_branch),
    campaign_service: DefaultCampaignService = Depends(get_campaign_service)
):
    try:
        # First check if campaign exists and belongs to this gym
        existing_campaign = await campaign_service.get_campaign(campaign_id)
        
        if not existing_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign with ID {campaign_id} not found"
            )
        
        # Make sure we have the Retell integration available in the API container
        call_service = getattr(campaign_service, "call_service", None)
        if not call_service or not getattr(call_service, "retell_integration", None):
            # For debugging: log what's missing or going wrong
            logger.error(f"Retell integration check failed: call_service={call_service is not None}, " +
                         f"retell_integration={getattr(call_service, 'retell_integration', None) is not None if call_service else 'N/A'}")
            
            # Return a clear error message
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Retell integration is not available. Cannot schedule calls. Check API container environment variables."
            )
            
        # Use current date if not specified
        if not target_date:
            target_date = date.today()
            
        # Schedule calls for the campaign
        try:
            # This might kick off a Celery task, need proper error handling
            scheduled_calls = await campaign_service.schedule_calls(campaign_id, target_date)
            
            return {
                "campaign_id": campaign_id,
                "scheduled_calls": scheduled_calls,
                "message": f"Successfully scheduled {len(scheduled_calls)} calls for {target_date}"
            }
        except Exception as schedule_error:
            logger.error(f"Error scheduling calls: {str(schedule_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error scheduling calls: {str(schedule_error)}"
            )
    except ValueError as e:
        # Handle validation errors (400 Bad Request)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions (keeps original status code)
        raise
    except Exception as e:
        # Handle unexpected errors (500 Internal Server Error)
        logger.error(f"Error scheduling calls for campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.put("/{campaign_id}/schedule", response_model=Dict[str, Any])
async def update_campaign_schedule(
    campaign_id: str = Path(..., description="The ID of the campaign to update schedule for"),
    schedule: CampaignSchedule = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    campaign_service: DefaultCampaignService = Depends(get_campaign_service)
):
    """
    Update the schedule configuration for a campaign.
    Only updates the schedule if the campaign belongs to the current user's gym.
    """
    try:
        # First check if campaign exists and belongs to this gym
        existing_campaign = await campaign_service.get_campaign(campaign_id)
        
        if not existing_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign with ID {campaign_id} not found"
            )
            
        # Verify campaign belongs to user's gym
        if str(existing_campaign.get("gym_id")) != str(current_gym.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or does not belong to your gym"
            )
            
        # Convert Pydantic model to dictionary
        schedule_data = schedule.dict()
        
        # Get current metrics or initialize if not exists
        metrics = existing_campaign.get("metrics", {}) or {}
        
        # Update schedule in metrics
        metrics["schedule"] = schedule_data
        
        # Update campaign with new metrics
        updated_campaign = await campaign_service.update_campaign(campaign_id, {"metrics": metrics})
        
        return {
            "message": "Campaign schedule updated successfully",
            "campaign_id": campaign_id,
            "schedule": metrics["schedule"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating schedule for campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
