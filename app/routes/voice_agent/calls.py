from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

# Import the database dependency and services
from backend.db.connections.database import get_db
from backend.services.call.factory import CallServiceFactory
from app.dependencies import get_current_user, User
import os

# Define request and response models
class InitiateCallRequest(BaseModel):
    phone_number: str
    lead_id: Optional[str] = None
    branch_id: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CallResponse(BaseModel):
    id: str
    status: str
    phone_number: str
    start_time: Optional[datetime] = None
    created_at: datetime

class CallStatusResponse(BaseModel):
    id: str
    status: str
    duration: Optional[int] = None
    transcription: Optional[str] = None
    recording_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

router = APIRouter()

# Get the telephony API URL from environment variables
TELEPHONY_API_URL = os.getenv("TELEPHONY_API_URL", "https://api.example.com/telephony")
TELEPHONY_API_KEY = os.getenv("TELEPHONY_API_KEY", "")

@router.post("/call", response_model=CallResponse)
async def initiate_call(
    call_request: InitiateCallRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate a new outbound call using the voice agent.
    """
    try:
        # Create the call service
        call_service = await CallServiceFactory.create_service(db)
        
        # Prepare call data
        call_data = {
            "phone_number": call_request.phone_number,
            "lead_id": call_request.lead_id,
            "branch_id": call_request.branch_id,
            "agent_user_id": current_user.id,
            "direction": "outbound",
            "status": "queued",
            "start_time": datetime.utcnow(),
            "metadata": call_request.metadata
        }
        
        # Create call record in database
        call = await call_service.create_call(call_data)
        
        # Initiate the call via the telephony provider
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEPHONY_API_URL}/calls",
                json={
                    "call_id": call.get("id"),
                    "to": call_request.phone_number,
                    "from": os.getenv("OUTBOUND_PHONE_NUMBER", "+15551234567"),
                    "agent_id": call_request.agent_id or "default_agent",
                    "webhook_url": os.getenv("WEBHOOK_BASE_URL", "https://api.example.com") + "/api/voice-agent/webhook"
                },
                headers={
                    "Authorization": f"Bearer {TELEPHONY_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            
            # Check if the call was successfully initiated
            if response.status_code != 200:
                # Update call status to failed
                await call_service.update_call_status(
                    call_id=call.get("id"),
                    status="failed",
                    metadata={"error": response.text}
                )
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to initiate call with telephony provider"
                )
                
            # Update call with provider's call SID
            provider_data = response.json()
            await call_service.update_call_status(
                call_id=call.get("id"),
                status="initiated",
                metadata={"provider_call_id": provider_data.get("call_sid")}
            )
        
        return {
            "id": call.get("id"),
            "status": "initiated",
            "phone_number": call_request.phone_number,
            "start_time": call.get("start_time"),
            "created_at": call.get("created_at")
        }
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log the error
        print(f"Error initiating call: {str(e)}")
        
        # Return a generic error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error initiating call"
        )

@router.get("/call/{call_id}/status", response_model=CallStatusResponse)
async def get_call_status(
    call_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status of an ongoing voice agent call.
    """
    try:
        # Create the call service
        call_service = await CallServiceFactory.create_service(db)
        
        # Get call from database
        call = await call_service.get_call_by_id(call_id)
        
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )
        
        # Check if the user has permission to view this call
        # In a real implementation, you would check if the call belongs to the user's gym
        if call.get("agent_user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this call"
            )
        
        return {
            "id": call.get("id"),
            "status": call.get("status"),
            "duration": call.get("duration"),
            "transcription": call.get("transcription"),
            "recording_url": call.get("recording_url"),
            "metadata": call.get("metadata", {})
        }
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log the error
        print(f"Error getting call status: {str(e)}")
        
        # Return a generic error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting call status"
        )

@router.post("/call/{call_id}/terminate")
async def terminate_call(
    call_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Terminate an ongoing voice agent call.
    """
    try:
        # Create the call service
        call_service = await CallServiceFactory.create_service(db)
        
        # Get call from database
        call = await call_service.get_call_by_id(call_id)
        
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )
        
        # Check if the user has permission to terminate this call
        if call.get("agent_user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to terminate this call"
            )
        
        # Check if the call is in a terminable state
        if call.get("status") in ["completed", "failed", "busy", "no-answer", "canceled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot terminate call in '{call.get('status')}' status"
            )
        
        # Terminate the call via the telephony provider
        provider_call_id = call.get("metadata", {}).get("provider_call_id")
        if not provider_call_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot terminate call without provider call ID"
            )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TELEPHONY_API_URL}/calls/{provider_call_id}/terminate",
                headers={
                    "Authorization": f"Bearer {TELEPHONY_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            
            # Check if the call was successfully terminated
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to terminate call with telephony provider"
                )
        
        # Update call status
        await call_service.update_call_status(
            call_id=call_id,
            status="canceled",
            metadata={"terminated_by_user_id": current_user.id}
        )
        
        return {"success": True, "message": "Call terminated successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log the error
        print(f"Error terminating call: {str(e)}")
        
        # Return a generic error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error terminating call"
        ) 