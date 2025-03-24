from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Import the database dependency and call service
from backend.db.connections.database import get_db
from backend.services.call.factory import CallServiceFactory
from app.dependencies import get_current_gym, Gym

# Define webhook payload models
class CallStatusUpdate(BaseModel):
    call_id: str
    status: str
    duration: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RecordingNotification(BaseModel):
    call_id: str
    recording_url: str
    duration: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

router = APIRouter()

@router.post("/webhook/inbound")
async def inbound_call_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint for handling inbound calls.
    
    This endpoint receives notifications from the telephony provider
    when a new inbound call is received.
    """
    try:
        # Parse the request body
        body = await request.json()
        
        # Create the call service
        call_service = await CallServiceFactory.create_service(db)
        
        # Process the inbound call
        call_data = {
            "call_sid": body.get("call_sid"),
            "from_number": body.get("from"),
            "to_number": body.get("to"),
            "direction": "inbound",
            "status": "received",
            "start_time": datetime.utcnow(),
        }
        
        # Create call record in database
        call = await call_service.create_call(call_data)
        
        # Return instructions for the voice agent
        return {
            "actions": [
                {
                    "action": "start_conversation",
                    "call_id": call.get("id"),
                    "ai_agent_id": "default_agent"
                }
            ]
        }
    except Exception as e:
        # Log the error
        print(f"Error processing inbound call webhook: {str(e)}")
        
        # Return a generic error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing inbound call"
        )

@router.post("/webhook/status")
async def call_status_webhook(
    status_update: CallStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint for receiving call status updates.
    
    This endpoint receives status updates from the telephony provider
    when a call's status changes (e.g., answered, completed, failed).
    """
    try:
        # Create the call service
        call_service = await CallServiceFactory.create_service(db)
        
        # Update call status in database
        await call_service.update_call_status(
            call_id=status_update.call_id,
            status=status_update.status,
            duration=status_update.duration,
            metadata=status_update.metadata
        )
        
        return {"success": True}
    except Exception as e:
        # Log the error
        print(f"Error processing call status webhook: {str(e)}")
        
        # Return a generic error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing call status update"
        )

@router.post("/webhook/recording")
async def recording_webhook(
    recording: RecordingNotification,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint for receiving call recording notifications.
    
    This endpoint receives notifications when a call recording is available.
    """
    try:
        # Create the call service
        call_service = await CallServiceFactory.create_service(db)
        
        # Update call with recording information
        await call_service.update_call_recording(
            call_id=recording.call_id,
            recording_url=recording.recording_url,
            duration=recording.duration
        )
        
        # Queue background task to transcribe the recording
        # Note: In a real implementation, you would use a task queue like Celery
        # await background_tasks.add_task(transcribe_recording, recording.call_id, recording.recording_url)
        
        return {"success": True}
    except Exception as e:
        # Log the error
        print(f"Error processing recording webhook: {str(e)}")
        
        # Return a generic error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing recording notification"
        ) 