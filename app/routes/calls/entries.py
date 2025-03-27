from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, status
from app.dependencies import get_current_user, get_current_gym, Gym, get_call_service
from typing import Optional
from datetime import datetime

from app.schemas.calls.base import CallCreate, CallUpdate
from app.schemas.calls.responses import CallListResponse, CallResponse, CallDetailResponse
from backend.services.call.implementation import DefaultCallService

router = APIRouter()

@router.get("", response_model=CallListResponse)
async def get_calls(
    current_gym: Gym = Depends(get_current_gym),
    lead_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
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
    # Convert string dates to datetime objects if provided
    start_datetime = datetime.fromisoformat(start_date) if start_date else None
    end_datetime = datetime.fromisoformat(end_date) if end_date else None
    
    # Determine which retrieval method to use based on provided filters
    # Priority: 1. lead_id, 2. campaign_id, 3. date range
    calls_data = []
    
    if lead_id:
        # If lead_id is provided, prioritize lead filtering
        calls_data = await call_service.get_calls_by_lead(lead_id, page, page_size=limit)
        
        # If campaign_id is also provided, filter further by campaign
        if campaign_id:
            calls_data = [call for call in calls_data if call.get("campaign_id") == campaign_id]
            
    elif campaign_id:
        # If only campaign_id is provided (no lead_id)
        calls_data = await call_service.get_calls_by_campaign(campaign_id, page, page_size=limit)
        
    else:
        # If neither lead_id nor campaign_id is provided, use date range filtering
        calls_data = await call_service.get_calls_by_date_range(
            current_gym.id, 
            start_datetime, 
            end_datetime,
            page, 
            page_size=limit
        )
    
    # Apply additional filters
    filtered_calls = calls_data
    
    # Filter by call type/direction if provided
    if direction:
        filtered_calls = [call for call in filtered_calls if call.get("call_type") == direction]
    
    # Filter by outcome if provided
    if outcome:
        filtered_calls = [call for call in filtered_calls if call.get("outcome") == outcome]
    
    # Return the filtered calls with pagination info
    return {
        "calls": filtered_calls,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(filtered_calls),
            "pages": (len(filtered_calls) + limit - 1) // limit if filtered_calls else 0
        }
    }

@router.get("/{call_id}", response_model=CallDetailResponse)
async def get_call(
    call_id: str = Path(..., description="The ID of the call to retrieve"),
    current_gym: Gym = Depends(get_current_gym),
    call_service: DefaultCallService = Depends(get_call_service)
):
    """
    Get detailed information about a specific call.
    Only returns the call if it belongs to the current user's gym.
    """
    try:
        # Get call details using the service
        call = await call_service.get_call(call_id)
        
        # Verify the call belongs to the current gym
        if call.get("gym_id") != str(current_gym.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found or does not belong to your gym"
            )
        
        return call
    except ValueError as e:
        # Handle case where call is not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("", response_model=CallResponse)
async def create_call(
    call: CallCreate = Body(...),
    current_gym: Gym = Depends(get_current_gym),
    call_service: DefaultCallService = Depends(get_call_service)
):
    """
    Schedule a new outbound call or record a manual inbound call.
    Automatically associates the call with the current user's gym.
    """
    # Implementation will be added later
    # In the actual implementation, you would:
    # 1. Create a new call object
    # 2. Set call.gym_id = current_gym.id
    pass

@router.patch("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: str = Path(..., description="The ID of the call to update"),
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
        existing_call = await call_service.get_call(call_id)
        
        # Verify the call belongs to the current gym
        if existing_call.get("gym_id") != str(current_gym.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found or does not belong to your gym"
            )
        
        # Update call using the service
        updated_call = await call_service.update_call(
            call_id=call_id,
            call_data=call_update.dict(exclude_unset=True)
        )
        return updated_call
    except ValueError as e:
        # Handle case where call is not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update call: {str(e)}"
        )