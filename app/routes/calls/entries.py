from fastapi import APIRouter, Depends, Query, Path, Body
from app.dependencies import get_current_user, get_current_gym, Gym
from typing import Optional

from app.schemas.calls.base import CallCreate, CallUpdate
from app.schemas.calls.responses import CallListResponse, CallResponse, CallDetailResponse

router = APIRouter()

@router.get("", response_model=CallListResponse)
async def get_calls(
    current_gym: Gym = Depends(get_current_gym),
    lead_id: Optional[str] = None,
    direction: Optional[str] = None,
    outcome: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get a paginated list of calls with optional filtering.
    Only returns calls from the current user's gym.
    """
    # Implementation will be added later
    # In the actual implementation, you would:
    # 1. Always filter by current_gym.id
    # 2. Apply additional filters (lead_id, direction, outcome, etc.)
    pass

@router.get("/{call_id}", response_model=CallDetailResponse)
async def get_call(
    call_id: str = Path(..., description="The ID of the call to retrieve"),
    current_gym: Gym = Depends(get_current_gym)
):
    """
    Get detailed information about a specific call.
    Only returns the call if it belongs to the current user's gym.
    """
    # Implementation will be added later
    # In the actual implementation, you would:
    # 1. Fetch the call by ID
    # 2. Verify it belongs to current_gym.id
    pass

@router.post("", response_model=CallResponse)
async def create_call(
    call: CallCreate = Body(...),
    current_gym: Gym = Depends(get_current_gym)
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
    current_gym: Gym = Depends(get_current_gym)
):
    """
    Update call details such as outcome, notes, or summary.
    Only updates the call if it belongs to the current user's gym.
    """
    # Implementation will be added later
    # In the actual implementation, you would:
    # 1. Fetch the call by ID
    # 2. Verify it belongs to current_gym.id
    pass 