"""
Campaign management routes.
"""
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, status
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

from app.schemas.campaigns.base import CampaignCreate, CampaignUpdate
from app.schemas.campaigns.responses import CampaignResponse, CampaignDetailResponse, CampaignListResponse
from app.dependencies import get_current_user, get_current_gym, get_current_branch, User, Gym, Branch, get_campaign_service
from backend.services.campaign.implementation import DefaultCampaignService

# Create router without prefix - this is important!
router = APIRouter()
logger = logging.getLogger(__name__)

def convert_campaign_uuids_to_str(campaign: dict) -> dict:
    """Convert UUID fields in a campaign dict to strings for FastAPI/Pydantic compatibility."""
    for key in ("id", "branch_id", "gym_id"):
        if isinstance(campaign.get(key), uuid.UUID):
            campaign[key] = str(campaign[key])
    return campaign

# Define routes directly on this router without additional prefix
@router.get("/", response_model=CampaignListResponse)
async def get_campaigns(
    current_branch: Branch = Depends(get_current_branch),
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    campaign_service: DefaultCampaignService = Depends(get_campaign_service)
):
    """
    Get a paginated list of campaigns with optional filtering.
    Only returns campaigns from the current user's branch.
    """
    try:
        filters = {}
        if status:
            filters["status"] = status
        if search:
            filters["search"] = search
            
        campaigns = await campaign_service.list_campaigns(
            branch_id=str(current_branch.id),
            filters=filters
        )
        
        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_campaigns = campaigns[start:end]

        # Convert UUIDs to strings for all campaigns in the response
        paginated_campaigns = [convert_campaign_uuids_to_str(c) for c in paginated_campaigns]

        return {
            "data": paginated_campaigns,
            "pagination": {
                "total": len(campaigns),
                "page": page,
                "limit": limit,
                "pages": (len(campaigns) + limit - 1) // limit
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving campaigns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
async def get_campaign(
    campaign_id: str = Path(..., description="The ID of the campaign to retrieve"),
    current_branch: Branch = Depends(get_current_branch),
    campaign_service: DefaultCampaignService = Depends(get_campaign_service)
):
    try:
        campaign = await campaign_service.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign with ID {campaign_id} not found"
            )
            
        # Verify campaign belongs to user's branch
        if str(campaign.get("branch_id")) != str(current_branch.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or does not belong to your branch"
            )
            
        # Get lead count
        campaign_leads = await campaign_service.get_campaign_leads(campaign_id)
        campaign["lead_count"] = len(campaign_leads)
        metrics = campaign.get("metrics", {}) or {}
        campaign["schedule"] = metrics.get("schedule", {})
        # Convert UUIDs to strings
        campaign = convert_campaign_uuids_to_str(campaign)
        return campaign
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    current_branch: Branch = Depends(get_current_branch),
    campaign_service: DefaultCampaignService = Depends(get_campaign_service)
):
    """
    Create a new campaign.
    Automatically associates the campaign with the current user's branch and gym.
    """
    try:
        # Convert Pydantic model to dictionary
        campaign_data = campaign.dict()

        # Add gym_id and branch_id from the dependencies
        campaign_data["gym_id"] = str(current_gym.id)
        campaign_data["branch_id"] = str(current_branch.id)

        # Set initial status
        campaign_data["campaign_status"] = "not_started"

        # Ensure metrics is a real dict (not a Pydantic model or None)
        metrics = campaign_data.get("metrics")
        if metrics is None:
            campaign_data["metrics"] = {}
        elif hasattr(metrics, "dict"):
            campaign_data["metrics"] = metrics.dict()
        else:
            campaign_data["metrics"] = dict(metrics)

        # Extract lead_ids if provided
        lead_ids = campaign_data.pop("lead_ids", None)

        # Create the campaign
        created_campaign = await campaign_service.create_campaign(campaign_data)
        # Convert UUIDs in response to strings for Pydantic validation
        created_campaign = convert_campaign_uuids_to_str(created_campaign)

        # If we have lead IDs, add them to the campaign
        if lead_ids:
            await campaign_service.add_leads_to_campaign(created_campaign["id"], lead_ids)

        return created_campaign
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def patch_campaign(
    campaign_id: str = Path(..., description="The ID of the campaign to update"),
    campaign: CampaignUpdate = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    campaign_service: DefaultCampaignService = Depends(get_campaign_service)
):
    """
    Partially update an existing campaign.
    Only updates the campaign if it belongs to the current user's gym.
    """
    try:
        # First check if campaign exists and belongs to this gym
        existing_campaign = await campaign_service.get_campaign(campaign_id)
        if not existing_campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaign with ID {campaign_id} not found"
            )
        if str(existing_campaign.get("gym_id")) != str(current_gym.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or does not belong to your gym"
            )
            
        # Convert Pydantic model to dictionary, excluding unset fields
        campaign_data = campaign.dict(exclude_unset=True)
        
        # Debug logging
        logger.info(f"PATCH campaign data before processing: {campaign_data}")
        
        # Handle metrics field specifically to avoid nesting issues
        if "metrics" in campaign_data:
            # Get current metrics to ensure we don't lose existing data
            current_metrics = existing_campaign.get("metrics", {}) or {}
            new_metrics = campaign_data["metrics"]
            
            # Handle the case where client sends a nested structure
            if isinstance(new_metrics, dict):
                # If it contains a schedule key, we need to merge it properly
                if "schedule" in new_metrics:
                    # Ensure current_metrics has a schedule dict
                    if "schedule" not in current_metrics:
                        current_metrics["schedule"] = {}
                    
                    # Update the schedule with new values
                    current_metrics["schedule"].update(new_metrics["schedule"])
                    
                # Update any other metrics keys
                for key, value in new_metrics.items():
                    if key != "schedule":  # We've already handled schedule specially
                        current_metrics[key] = value
                
                # Set the merged metrics back to campaign_data
                campaign_data["metrics"] = current_metrics
            
            # Log the processed metrics for debugging
            logger.info(f"Processed metrics: {campaign_data['metrics']}")
        
        # Update the campaign
        updated_campaign = await campaign_service.update_campaign(campaign_id, campaign_data)
        updated_campaign = convert_campaign_uuids_to_str(updated_campaign)
        return updated_campaign
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error patching campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str = Path(..., description="The ID of the campaign to delete"),
    current_gym: Gym = Depends(get_current_gym),
    campaign_service: DefaultCampaignService = Depends(get_campaign_service)
):
    """
    Delete a campaign.
    Only deletes the campaign if it belongs to the current user's gym.
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
            
        # Delete the campaign
        result = await campaign_service.delete_campaign(campaign_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete campaign"
            )
            
        # No UUIDs to convert in delete response
        return {"message": "Campaign successfully deleted"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str = Path(..., description="The ID of the campaign to pause"),
    current_gym: Gym = Depends(get_current_gym),
    campaign_service: DefaultCampaignService = Depends(get_campaign_service)
):
    """
    Pause a campaign.
    Only pauses the campaign if it belongs to the current user's gym.
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
            
        # Update campaign status to paused
        updated_campaign = await campaign_service.update_campaign(campaign_id, {"campaign_status": "paused"})
        updated_campaign = convert_campaign_uuids_to_str(updated_campaign)
        return {"message": "Campaign paused successfully", "campaign": updated_campaign}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error pausing campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/{campaign_id}/cancel")
async def cancel_campaign(
    campaign_id: str = Path(..., description="The ID of the campaign to cancel"),
    current_gym: Gym = Depends(get_current_gym),
    campaign_service: DefaultCampaignService = Depends(get_campaign_service)
):
    """
    Cancel a campaign.
    Only cancels the campaign if it belongs to the current user's gym.
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
            
        # Cancel the campaign
        cancelled_campaign = await campaign_service.cancel_campaign(campaign_id)
        cancelled_campaign = convert_campaign_uuids_to_str(cancelled_campaign)
        return {"message": "Campaign cancelled successfully", "campaign": cancelled_campaign}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error cancelling campaign {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
