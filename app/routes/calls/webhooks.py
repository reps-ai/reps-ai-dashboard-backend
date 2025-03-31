from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any
import json
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.connections.database import get_db
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository
from backend.integrations.retell.implementation import RetellImplementation

router = APIRouter()

@router.post("/retell-webhook")
async def handle_retell_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    """
    Handle webhooks from Retell for call events
    """
    try:
        # Get the raw webhook payload
        payload = await request.json()
        
        # Process webhook with retell implementation
        retell_client = RetellImplementation()
        processed_data = await retell_client.process_webhook(payload)
        
        if processed_data.get("status") == "error":
            return {
                "status": "error",
                "message": processed_data.get("message", "Error processing webhook")
            }
        
        # Initialize call repository
        call_repo = PostgresCallRepository(session)
        
        # Get event type
        event_type = processed_data.get("event_type")
        call_id = processed_data.get("call_id")
        
        # Check for existing call by external ID (Retell call_id)
        existing_call = await call_repo.get_call_by_external_id(call_id)
        
        if event_type == "call_started":
            # Handle call started event
            if existing_call:
                # Update existing call
                update_data = {
                    "call_status": "in_progress",
                    "start_time": datetime.fromtimestamp(processed_data.get("timestamp", 0) / 1000) if processed_data.get("timestamp") else None,
                }
                return await call_repo.update_call(existing_call["id"], update_data)
            else:
                # We can't create a call without lead_id, branch_id, and gym_id
                # These should be in the metadata from the call creation
                metadata = processed_data.get("raw_data", {}).get("metadata", {})
                
                if not metadata.get("lead_id") or not metadata.get("branch_id") or not metadata.get("gym_id"):
                    return {
                        "status": "error",
                        "message": "Missing required metadata for call creation"
                    }
                
                # Create new call
                call_data = {
                    "lead_id": metadata.get("lead_id"),
                    "branch_id": metadata.get("branch_id"),
                    "gym_id": metadata.get("gym_id"),
                    "call_type": processed_data.get("raw_data", {}).get("direction", "outbound"),
                    "call_status": "in_progress",
                    "start_time": datetime.fromtimestamp(processed_data.get("timestamp", 0) / 1000) if processed_data.get("timestamp") else None,
                    "campaign_id": metadata.get("campaign_id"),
                    "external_call_id": call_id  # Store Retell call_id as external_id
                }
                return await call_repo.create_call(call_data)
                
        elif event_type == "call_ended":
            # Handle call ended event
            if not existing_call:
                return {
                    "status": "error",
                    "message": f"Call with external ID {call_id} not found"
                }
            
            # Update call with end time, duration, recording, transcript
            update_data = {
                "call_status": "completed",
                "end_time": datetime.fromtimestamp(processed_data.get("timestamp", 0) / 1000) if processed_data.get("timestamp") else None,
                "duration": processed_data.get("duration"),
                "recording_url": processed_data.get("raw_data", {}).get("recording_url"),
                "transcript": processed_data.get("raw_data", {}).get("transcript")
            }
            return await call_repo.update_call(existing_call["id"], update_data)
            
        elif event_type == "call_analyzed":
            # Handle call analyzed event
            if not existing_call:
                return {
                    "status": "error",
                    "message": f"Call with external ID {call_id} not found"
                }
            
            # Update call with analysis data
            update_data = {
                "summary": processed_data.get("summary"),
                "sentiment": processed_data.get("sentiment"),
                # Set outcome based on call success
                "outcome": "scheduled" if processed_data.get("successful") else "not_interested"
            }
            return await call_repo.update_call(existing_call["id"], update_data)
            
        else:
            # Unknown event type
            return {
                "status": "success",
                "message": f"Received unknown event type: {event_type}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing webhook: {str(e)}"
        } 