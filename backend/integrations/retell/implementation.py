from .interface import RetellIntegration
from retell import Retell
import os
import json
from typing import Dict, Any, List, Optional
import asyncio
import uuid

class RetellImplementation(RetellIntegration):
    """
    Implementation of the Retell Integration Service.
    """
    
    def __init__(self):
        """Initialize the Retell client with API key from environment variables."""
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
        # For Retell, authentication is handled at client initialization
        # This method serves as a validation check
        try:
            # We could make a simple API call to validate the key
            # For now, we'll just return a success message
            return {"status": "success", "message": "API key is set"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def create_call(
        self, 
        lead_data: Dict[str, Any], 
        campaign_id: Optional[uuid.UUID] = None,
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
            to_number = lead_data.get("phone_number") or lead_data.get("phone")
            if not to_number:
                raise ValueError("Lead data does not contain a valid phone number")
                
            # Clean phone number if needed (remove non-numeric characters)
            if isinstance(to_number, str):
                to_number = ''.join(filter(str.isdigit, to_number))
                
            # Ensure it's at least 10 digits
            if len(to_number) < 10:
                raise ValueError(f"Phone number {to_number} is too short (min 10 digits)")
            
            # Get the 'from' number from environment variables
            from_number = os.getenv("RETELL_FROM_NUMBER")
            if not from_number:
                raise ValueError("RETELL_FROM_NUMBER environment variable is required")
            
            # Prepare call parameters
            call_params = {
                "from_number": from_number,
                "to_number": to_number,
            }
            
            # Add optional parameters
            if max_duration:
                call_params["max_call_duration_ms"] = max_duration * 1000
                
            # Add metadata from lead and campaign
            metadata = {}
            if lead_data:
                # Convert all UUID objects to strings for metadata
                lead_id = lead_data.get("id")
                if lead_id:
                    metadata["lead_id"] = str(lead_id)
                    
                metadata["lead_name"] = lead_data.get("name") or "Unknown"
                
                gym_id = lead_data.get("gym_id")
                if gym_id:
                    metadata["gym_id"] = str(gym_id)
                    
                branch_id = lead_data.get("branch_id")
                if branch_id:
                    metadata["branch_id"] = str(branch_id)
                
            if campaign_id:
                metadata["campaign_id"] = str(campaign_id)
                
            if metadata:
                call_params["metadata"] = metadata
            
            # Create comprehensive client_data object with all non-null lead information
            client_data = {}
            
            # List of fields to check and include if not null (db_field, display_field)
            fields_to_include = [
                ("first_name", "first_name"),
                ("last_name", "last_name"),
                ("notes", "notes"),
                ("interest", "interest"),
                ("interest_location", "interest_location"),
                ("last_conversation_summary", "last_conversation_summary"),
                ("score", "score"),
                ("source", "source"),
                ("fitness_goals", "fitness_goals"),
                ("budget_range", "budget_range"),
                ("timeframe", "timeframe"),
                ("preferred_contact_method", "contact_method"),
                ("preferred_contact_time", "contact_time"),
                ("urgency", "urgency_level"),
                ("qualification_score", "qual_score"),
                ("qualification_notes", "qual_notes"),
                ("fitness_level", "fitness_level"),
                ("previous_gym_experience", "has_gym_experience"),
                ("specific_health_goals", "specific_health_goals"),
                ("preferred_training_type", "training_type"),
                ("availability", "availability"),
                ("medical_conditions", "medical_conditions")
            ]
            
            # Only add non-null values to client_data
            for db_field, display_field in fields_to_include:
                if lead_data.get(db_field) is not None:
                    # Convert boolean values to strings for better LLM interpretation
                    if isinstance(lead_data.get(db_field), bool):
                        client_data[display_field] = "Yes" if lead_data.get(db_field) else "No"
                    else:
                        client_data[display_field] = lead_data.get(db_field)
            
            # Add dynamic variables for the agent
            dynamic_vars = {}
            
            # Add name if available
            full_name = ""
            if lead_data.get("first_name"):
                full_name += lead_data.get("first_name")
            if lead_data.get("last_name"):
                full_name += " " + lead_data.get("last_name") if full_name else lead_data.get("last_name")
            
            if full_name:
                dynamic_vars["customer_name"] = full_name
            
            # Add the client_data object if it has any values
            if client_data:
                # Convert client_data to a JSON string as required by Retell
                dynamic_vars["client_data"] = json.dumps(client_data)
                
            if dynamic_vars:
                call_params["retell_llm_dynamic_variables"] = dynamic_vars
                
            # Log the parameters we're sending to Retell
            print(f"Creating Retell call with parameters: {call_params}")
            
            # Make the API call to create the phone call
            # Update to use llm_id instead of agent_id in the API call
                
            response = self.client.call.create_phone_call(**call_params)
            
            # Convert response to dictionary
            if not isinstance(response, dict):
                # Convert the response object to a dictionary
                response_dict = {
                    "call_id": response.call_id,
                    "agent_id": response.agent_id,
                    "call_status": response.call_status,
                    "metadata": response.metadata
                }
            else:
                response_dict = response
            
            # Add additional context
            response_dict["lead_data"] = lead_data
            if campaign_id:
                response_dict["campaign_id"] = str(campaign_id)
            
            return response_dict
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "lead_data": lead_data
            }

    async def create_and_log_call(
        self, 
        lead_data: Dict[str, Any], 
        campaign_id: Optional[uuid.UUID] = None,
        max_duration: Optional[int] = None,
        call_repository = None
    ) -> Dict[str, Any]:
        """
        Create a call in Retell and log it in the application database.
        
        Args:
            lead_data: Dictionary containing lead information
            campaign_id: Optional ID of the campaign
            max_duration: Optional maximum duration in seconds
            call_repository: Optional repository for creating call logs
            
        Returns:
            Dictionary containing call details
        """
        try:
            # Create the call in Retell
            retell_response = await self.create_call(lead_data, campaign_id, max_duration)
            
            if retell_response.get("status") == "error":
                return retell_response
            
            # If call repository is provided, update the call log
            if call_repository:
                # Get the call_id from the retell response
                external_call_id = retell_response.get("call_id")
                if not external_call_id:
                    return {
                        "status": "error",
                        "message": "No call ID returned from Retell",
                        "retell_response": retell_response
                    }
                
                # Update the existing call with Retell's external ID
                # The implementation expects that a call record was already created in trigger_call
                # before calling this method
                
                # Find the call we need to update
                # Note: We don't have the internal call ID here, but we can use the lead_id and timestamp
                # to identify the most recent call for this lead
                lead_id = lead_data.get("id")
                if not isinstance(lead_id, uuid.UUID):
                    # Convert to UUID if it's not already
                    try:
                        lead_id = uuid.UUID(str(lead_id))
                    except ValueError:
                        return {
                            "status": "error", 
                            "message": f"Invalid lead_id format: {lead_id}"
                        }
                
                calls_result = await call_repository.get_calls_by_lead(lead_id, page=1, page_size=1)
                calls = calls_result.get("calls", [])
                
                if not calls:
                    # If no existing call is found (shouldn't happen in normal flow), log a warning
                    return {
                        "status": "warning",
                        "message": "No existing call found to update with Retell information",
                        "external_call_id": external_call_id,
                        "lead_id": str(lead_id),
                        "call_status": retell_response.get("call_status", "initiated")
                    }
                
                internal_call_id = calls[0].get("id")
                if not isinstance(internal_call_id, uuid.UUID):
                    # Convert to UUID if it's not already
                    try:
                        internal_call_id = uuid.UUID(str(internal_call_id))
                    except ValueError:
                        return {
                            "status": "error", 
                            "message": f"Invalid internal_call_id format: {internal_call_id}"
                        }
                
                # Update the call in the database with Retell information
                call_update_data = {
                    "external_call_id": external_call_id,
                    "call_status": retell_response.get("call_status", "initiated")
                }
                
                updated_call = await call_repository.update_call(internal_call_id, call_update_data)
                
                # Combine responses
                result = {
                    **retell_response,
                    "call_id": str(internal_call_id),
                    "call_status": updated_call.get("call_status")
                }
                
                return result
            
            return retell_response
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "lead_data": lead_data
            }


    async def get_call_recording(self, call_id: str) -> Dict[str, Any]:
        """
        Get the recording for a call.
        
        Args:
            call_id: ID of the call
            
        Returns:
            Dictionary containing recording information
        """
        try:
            # First get call details which include recording URL
            call_details = await self.get_call_status(call_id)
            
            if call_details.get("status") == "error":
                return call_details
                
            # Extract recording URL
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
        """
        Get the transcript for a call.
        
        Args:
            call_id: ID of the call
            
        Returns:
            List of transcript entries
        """
        try:
            # First get call details which include transcript
            call_details = await self.get_call_status(call_id)
            
            if call_details.get("status") == "error":
                return []
                
            # Extract transcript
            transcript_object = call_details.get("transcript_object", [])
            
            # If transcript_object is not available, try to parse the transcript string
            if not transcript_object and call_details.get("transcript"):
                # Simple parsing of the transcript string
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
        """
        Process a webhook from Retell.
        
        Args:
            webhook_data: Dictionary containing webhook data
            
        Returns:
            Dictionary containing processed webhook result
        """
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
                    "event_type": "call_started",
                    "call_id": call_id,
                    "call_status": "in_progress",
                    "timestamp": call_data.get("start_timestamp"),
                    "raw_data": call_data
                }
                
            elif event == "call_ended":
                return {
                    "event_type": "call_ended",
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
                    "event_type": "call_analyzed",
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