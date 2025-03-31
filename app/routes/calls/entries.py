from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, status
from app.dependencies import get_current_user, get_current_gym, Gym, get_call_service, get_current_branch, Branch
from typing import Optional
from datetime import datetime
import uuid
import logging

from app.schemas.calls.base import CallCreate, CallUpdate
from app.schemas.calls.responses import CallListResponse, CallResponse, CallDetailResponse
from backend.services.call.implementation import DefaultCallService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=CallListResponse)
async def get_calls(
    current_gym: Gym = Depends(get_current_gym),
    lead_id: Optional[uuid.UUID] = None,
    campaign_id: Optional[uuid.UUID] = None,
    direction: Optional[str] = None,
    outcome: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    call_service: DefaultCallService = Depends(get_call_service)
):
    """
    Get a paginated list of calls with optional filtering.
    Only returns calls from the current user's gym.
    Supports filtering by lead_id, campaign_id, direction, outcome, and date range.
    Multiple filters can be applied simultaneously.
    """
    try:
        # Convert string dates to datetime objects if provided
        start_datetime = datetime.fromisoformat(start_date) if start_date else None
        end_datetime = datetime.fromisoformat(end_date) if end_date else None
        
        # Use the service function for filtering calls
        result = await call_service.get_filtered_calls(
            gym_id=str(current_gym.id),
            page=page,
            page_size=limit,
            lead_id=lead_id,
            campaign_id=campaign_id,
            direction=direction,
            outcome=outcome,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        # Check if any calls were found and return 404 if none match the criteria
        if not result.get("calls"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No calls found matching the specified criteria"
            )
            
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/{call_id}", response_model=CallDetailResponse)
async def get_call(
    call_id: uuid.UUID = Path(..., description="The ID of the call to retrieve"),
    current_gym: Gym = Depends(get_current_gym),
    call_service: DefaultCallService = Depends(get_call_service)
):
    """
    Get detailed information about a specific call.
    Only returns the call if it belongs to the current user's gym.
    """
    try:
        # The service layer handles exceptions
        call = await call_service.get_call(call_id)
        
        # Security check: verify the call belongs to the current gym
        if str(call.get("gym_id")) != str(current_gym.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found or does not belong to your gym"
            )
        
        return call
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/")
async def create_call(
    lead_id: uuid.UUID = Body(..., embed=True, description="The ID of the lead to call"),
    current_gym: Gym = Depends(get_current_gym),
    current_branch: Branch = Depends(get_current_branch),
    call_service: DefaultCallService = Depends(get_call_service)
):
    """
    Schedule a new outbound call to a lead.
    Automatically associates the call with the current gym and branch.
    """
    try:
        # Log the incoming call request
        logger.info(f"Creating call to lead: {lead_id}")
        
        # Call trigger_call service method with only lead_id
        return await call_service.trigger_call(
            lead_id=lead_id,
            # The service will handle creating appropriate call data with the gym and branch
            # from the current context
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.patch("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: uuid.UUID = Path(..., description="The ID of the call to update"),
    call_update: CallUpdate = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    call_service: DefaultCallService = Depends(get_call_service)
):
    """
    Update call details such as outcome, notes, or summary.
    Only updates the call if it belongs to the current user's gym.
    """
    try:
        # First get the call to verify ownership
        call = await call_service.get_call(call_id)
        
        # Verify the call belongs to the current gym
        if str(call.get("gym_id")) != str(current_gym.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found or does not belong to your gym"
            )
        
        # Update call using the service
        return await call_service.update_call(
            call_id=call_id,
            call_data=call_update.dict(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.delete("/{call_id}", response_model=dict)
async def delete_call(
    call_id: uuid.UUID = Path(..., description="The ID of the call to delete"),
    current_gym: Gym = Depends(get_current_gym),
    call_service: DefaultCallService = Depends(get_call_service)
):
    """
    Delete a call record.
    Only deletes the call if it belongs to the current user's gym.
    """
    try:
        # First get the call to verify ownership
        call = await call_service.get_call(call_id)
        
        # Verify the call belongs to the current gym
        if str(call.get("gym_id")) != str(current_gym.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found or does not belong to your gym"
            )
        
        # Delete call using the service
        return await call_service.delete_call(call_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )