"""
Implementation of the Retell Integration Service.
"""
from .interface import RetellIntegration
from retell import Retell
import os
import json
from typing import Dict, Any, List, Optional
import asyncio

class RetellImplementation(RetellIntegration):
    """
    Implementation of the Retell Integration Service.
    """
    
    def __init__(self):
        """Initialize the Retell client with API key from environment variables."""
        self.base_url = "https://api.retell.ai/v1"
        self.api_key = os.getenv("RETELL_API_KEY")
        
        if not self.api_key:
            raise ValueError("RETELL_API_KEY environment variable is required")
            
        self.client = Retell(api_key=self.api_key)

    async def authenticate(self) -> Dict[str, Any]:
        """
        Authenticate with the Retell API.
        
        Returns:
            Dictionary containing authentication result
        """
        try:
            return {"status": "success", "message": "API key is set"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def create_call(
        self, 
        lead_data: Dict[str, Any], 
        campaign_id: Optional[str] = None,
        max_duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a call in Retell.
        
        Args:
            lead_data: Dictionary containing lead information
            campaign_id: Optional ID of the campaign
            max_duration: Optional maximum duration in seconds
            
        Returns:
            Dictionary containing call details
        """
        try:
            # Extract phone number from lead data
            to_number = lead_data.get("phone_number")
            if not to_number:
                raise ValueError("Lead data does not contain a valid phone number")
            
            # Get the 'from' number from environment variables
            from_number = os.getenv("RETELL_FROM_NUMBER")
            if not from_number:
                raise ValueError("RETELL_FROM_NUMBER environment variable is required")
            
            # Prepare call parameters (only required fields)
            call_params = {
                "from_number": from_number,
                "to_number": to_number,
            }
            
            # Add metadata from lead and campaign
            metadata = {}
            if lead_data:
                metadata["lead_id"] = lead_data.get("id")
                metadata["lead_name"] = lead_data.get("name")
                metadata["gym_id"] = lead_data.get("gym_id")
                metadata["branch_id"] = lead_data.get("branch_id")
                
            if campaign_id:
                metadata["campaign_id"] = campaign_id
                
            if metadata:
                call_params["metadata"] = metadata
            
            # Make the API call to create the phone call
            response = self.client.call.create_phone_call(**call_params)
            
            # Convert response to dictionary
            if not isinstance(response, dict):
                response_dict = {
                    "call_id": response.call_id,
                    "call_status": response.call_status if hasattr(response, 'call_status') and response.call_status is not None else "registered",
                    "metadata": response.metadata
                }
            else:
                response_dict = response
                # Ensure response has a call_status
                if "call_status" not in response_dict or response_dict["call_status"] is None:
                    response_dict["call_status"] = "registered"
            
            # Add additional context
            response_dict["lead_data"] = lead_data
            if campaign_id:
                response_dict["campaign_id"] = campaign_id
            
            return response_dict
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "lead_data": lead_data
            }

    async def get_call_recording(self, call_id: str) -> Dict[str, Any]:
        """Get recording for a call."""
        try:
            # First get call details which include recording URL
            call_details = await self.get_call_status(call_id)
            
            if call_details.get("status") == "error":
                return call_details
                
            recording_url = call_details.get("recording_url")
            if not recording_url:
                return {
                    "status": "error",
                    "message": "Recording not available for this call",
                    "call_id": call_id
                }
                
            return {
                "call_id": call_id,
                "recording_url": recording_url,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "call_id": call_id
            }

    async def get_call_transcript(self, call_id: str) -> List[Dict[str, Any]]:
        """Get transcript for a call."""
        try:
            # First get call details which include transcript
            call_details = await self.get_call_status(call_id)
            
            if call_details.get("status") == "error":
                return []
                
            # Extract transcript
            transcript_object = call_details.get("transcript_object", [])
            
            # If transcript_object is not available, try to parse the transcript string
            if not transcript_object and call_details.get("transcript"):
                transcript_string = call_details.get("transcript", "")
                lines = transcript_string.strip().split("\n")
                
                parsed_transcript = []
                for line in lines:
                    if ":" in line:
                        parts = line.split(":", 1)
                        role = "agent" if "Agent" in parts[0] else "user"
                        content = parts[1].strip()
                        parsed_transcript.append({
                            "role": role,
                            "content": content
                        })
                
                return parsed_transcript
                
            return transcript_object
            
        except Exception as e:
            return []

    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a webhook from Retell."""
        try:
            # Extract event type and call data
            event = webhook_data.get("event")
            call_data = webhook_data.get("call", {})
            call_id = call_data.get("call_id")
            
            if not event or not call_id:
                return {
                    "status": "error",
                    "message": "Invalid webhook data, missing event or call_id",
                    "webhook_data": webhook_data
                }
            
            # Process different event types
            if event == "call_started":
                return {
                    "event_type": "call.started",
                    "call_id": call_id,
                    "call_status": "in_progress",
                    "timestamp": call_data.get("start_timestamp"),
                    "raw_data": call_data
                }
                
            elif event == "call_ended":
                return {
                    "event_type": "call.ended",
                    "call_id": call_id,
                    "call_status": "completed",
                    "duration": (call_data.get("end_timestamp", 0) - call_data.get("start_timestamp", 0)) / 1000 if call_data.get("start_timestamp") else 0,
                    "timestamp": call_data.get("end_timestamp"),
                    "recording_url": call_data.get("recording_url"),
                    "transcript": call_data.get("transcript"),
                    "raw_data": call_data
                }
                
            elif event == "call_analyzed":
                # Process post-call analysis data
                analysis = call_data.get("call_analysis", {})
                
                return {
                    "event_type": "call.analyzed",
                    "call_id": call_id,
                    "summary": analysis.get("call_summary"),
                    "sentiment": analysis.get("user_sentiment"),
                    "successful": analysis.get("call_successful", False),
                    "custom_data": analysis.get("custom_analysis_data", {}),
                    "raw_data": call_data
                }
            else:
                return {
                    "event_type": "unknown",
                    "call_id": call_id,
                    "original_event": event,
                    "raw_data": call_data
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "webhook_data": webhook_data
            }
