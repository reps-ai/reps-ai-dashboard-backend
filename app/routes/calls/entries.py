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
    current_branch: Branch = Depends(get_current_branch),  # Branch from token
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
    Only returns calls from the current user's branch.
    Supports filtering by lead_id, campaign_id, direction, outcome, and date range.
    Multiple filters can be applied simultaneously.
    """
    try:
        # Convert string dates to datetime objects if provided
        start_datetime = None
        end_datetime = None
        
        try:
            if start_date:
                start_datetime = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start date format. Use ISO format (YYYY-MM-DD)."
            )
        
        try:
            if end_date:
                end_datetime = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end date format. Use ISO format (YYYY-MM-DD)."
            )
        
        # Use the service function for filtering calls
        # Note: using branch_id instead of gym_id parameter
        result = await call_service.get_filtered_calls(
            branch_id=str(current_branch.id),  # Changed from gym_id to branch_id
            page=page,
            page_size=limit,
            lead_id=lead_id,
            campaign_id=campaign_id,
            direction=direction,
            outcome=outcome,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        # Remove the empty result check and just return the result
        # Empty arrays are valid API responses
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
    call_id: str = Path(..., description="The ID of the call to retrieve"),
    current_branch: Branch = Depends(get_current_branch),  # Change to branch dependency
    call_service: DefaultCallService = Depends(get_call_service)
):
    """
    Get detailed information about a specific call.
    Only returns the call if it belongs to the current user's branch.
    """
    try:
        # Convert string to UUID (this will raise ValueError if invalid)
        try:
            call_id_uuid = uuid.UUID(call_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid call ID format. Must be a valid UUID."
            )
        
        # The service layer handles exceptions
        try:
            call = await call_service.get_call(call_id_uuid)
            
            # If we got here but call is None, handle as not found
            if call is None:
                logger.warning(f"Call not found with ID: {call_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Call with ID {call_id} not found"
                )
                
            # Security check: verify the call belongs to the current branch
            if str(call.get("branch_id")) != str(current_branch.id):
                logger.warning(f"Call {call_id} does not belong to branch {current_branch.id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Call not found or does not belong to your branch"
                )
            
            return call
        except ValueError as e:
            logger.error(f"Value error when retrieving call {call_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e) if str(e) else "Call not found"
            )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Improved error logging
        error_msg = str(e) if str(e) else "Unknown database error occurred"
        logger.exception(f"Error retrieving call {call_id}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {error_msg}"
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
        
        # Pass all needed context to the service
        return await call_service.trigger_call(
            lead_id=lead_id,
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
    call_id: str = Path(..., description="The ID of the call to update"),
    call_update: CallUpdate = Body(...),
    current_branch: Branch = Depends(get_current_branch),
    call_service: DefaultCallService = Depends(get_call_service)
):
    """
    Update call details such as outcome, notes, or summary.
    Only updates the call if it belongs to the current user's branch.
    """
    try:
        # Log the update attempt
        logger.info(f"Attempting to update call {call_id} with data: {call_update.dict(exclude_unset=True)}")
        
        # Convert string to UUID (this will raise ValueError if invalid)
        try:
            call_id_uuid = uuid.UUID(call_id)
        except ValueError:
            logger.warning(f"Invalid call ID format: {call_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid call ID format. Must be a valid UUID."
            )
            
        # First get the call to verify ownership
        try:
            call = await call_service.get_call(call_id_uuid)
            
            # If call is None, handle as not found
            if call is None:
                logger.warning(f"Call not found with ID: {call_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Call with ID {call_id} not found"
                )
            
            # Verify the call belongs to the current branch
            if str(call.get("branch_id")) != str(current_branch.id):
                logger.warning(f"Call {call_id} does not belong to branch {current_branch.id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Call not found or does not belong to your branch"
                )
            
            # Update call using the service
            try:
                call_data = call_update.dict(exclude_unset=True)
                logger.debug(f"Updating call {call_id} with data: {call_data}")
                updated_call = await call_service.update_call(
                    call_id=call_id_uuid,
                    call_data=call_data
                )
                logger.info(f"Successfully updated call {call_id}")
                return updated_call
            except ValueError as e:
                error_msg = str(e) if str(e) else "Invalid update data provided"
                logger.error(f"Value error updating call {call_id}: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            except Exception as e:
                error_msg = str(e) if str(e) else "Unknown error during update"
                logger.exception(f"Error updating call {call_id}: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update call: {error_msg}"
                )
        except ValueError as e:
            logger.error(f"Value error when retrieving call {call_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e) if str(e) else "Call not found"
            )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown server error"
        logger.exception(f"Unexpected error in update_call endpoint for {call_id}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {error_msg}"
        )

@router.delete("/{call_id}", response_model=dict)
async def delete_call(
    call_id: str = Path(..., description="The ID of the call to delete"),
    current_branch: Branch = Depends(get_current_branch),  # Change to branch dependency
    call_service: DefaultCallService = Depends(get_call_service)
):
    """
    Delete a call record.
    Only deletes the call if it belongs to the current user's branch.
    """
    try:
        # Log deletion attempt
        logger.info(f"Attempting to delete call with ID: {call_id}")
        
        # Convert string to UUID (this will raise ValueError if invalid)
        try:
            call_id_uuid = uuid.UUID(call_id)
        except ValueError:
            logger.warning(f"Invalid call ID format for deletion: {call_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid call ID format. Must be a valid UUID."
            )
            
        # First get the call to verify ownership
        try:
            call = await call_service.get_call(call_id_uuid)
            
            # If call is None, handle as not found
            if call is None:
                logger.warning(f"Call not found for deletion with ID: {call_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Call with ID {call_id} not found"
                )
            
            # Verify the call belongs to the current branch
            if str(call.get("branch_id")) != str(current_branch.id):
                logger.warning(f"Call {call_id} does not belong to branch {current_branch.id} - deletion denied")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Call not found or does not belong to your branch"
                )
            
            # Delete call using the service
            try:
                logger.debug(f"Proceeding with deletion of call {call_id}")
                result = await call_service.delete_call(call_id_uuid)
                logger.info(f"Successfully deleted call {call_id}")
                return result
            except ValueError as e:
                error_msg = str(e) if str(e) else "Invalid data for deletion"
                logger.error(f"Value error deleting call {call_id}: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            except Exception as e:
                error_msg = str(e) if str(e) else "Unknown error during deletion"
                logger.exception(f"Error deleting call {call_id}: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete call: {error_msg}"
                )
        except ValueError as e:
            logger.error(f"Value error when retrieving call {call_id} before deletion: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=str(e) if str(e) else "Call not found"
            )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown server error"
        logger.exception(f"Unexpected error in delete_call endpoint for {call_id}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {error_msg}"
        )