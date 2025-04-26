"""
Implementation of the Call Management Service.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid
from .interface import CallService
from ...db.repositories.call import CallRepository
from ...utils.logging.logger import get_logger
from ...integrations.retell.interface import RetellIntegration
from ...db.models.call.call_log import CallLog  # Import the CallLog model for type hints
from ...db.helpers.lead.lead_queries import get_lead_with_related_data
logger = get_logger(__name__)

class DefaultCallService(CallService):
    """
    Default implementation of the Call Management Service.
    """
    
    def __init__(self, call_repository: CallRepository, retell_integration: RetellIntegration = None):
        """
        Initialize the call service.
        
        Args:
            call_repository: Repository for call operations
            retell_integration: Optional Retell integration service
        """
        self.call_repository = call_repository
        self.retell_integration = retell_integration
    
    #Aditya
    async def trigger_call(self, lead_id: uuid.UUID, campaign_id: Optional[uuid.UUID] = None, lead_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Trigger a call to a lead.
        
        Args:
            lead_id: ID of the lead to call
            campaign_id: Optional ID of the campaign (defaults to None)
            lead_data: Optional pre-loaded lead data (defaults to None)
            
        Returns:
            Dictionary containing call details
            
        Raises:
            ValueError: If there's an error triggering the call
        """
        try:
            logger.info(f"Triggering call to lead: {lead_id}")
            lead_data = await get_lead_with_related_data(self.call_repository.session, lead_id)
            # Create basic call data with valid IDs - simplifying to just what we need
            call_data = {
                "lead_id": lead_id,  # Already UUID
                "gym_id": lead_data["gym_id"],  # Valid gym ID
                "branch_id": lead_data["branch_id"],  # Valid branch ID
                "call_status": "scheduled",
                "call_type": "outbound",
                "created_at": datetime.now(),
                "start_time": datetime.now()
            }
            
            # Only set campaign_id if one is explicitly provided
            if campaign_id:
                call_data["campaign_id"] = campaign_id
            
            # Log the data we're inserting
            logger.info(f"Creating call with data: {call_data}")
            
            # Create call record in database
            db_call = await self.call_repository.create_call(call_data)
            logger.info(f"Created call record with ID: {db_call.get('id')}")
            
            # If Retell integration is available, trigger the call
            if self.retell_integration:
                try:
                    # Make the call using Retell with comprehensive lead data
                    retell_call_result = await self.retell_integration.create_call(
                        lead_data=lead_data,  # Pass the full lead data object
                        campaign_id=call_data.get("campaign_id")  # Pass campaign_id only if it exists
                    )
                    
                    if retell_call_result.get("status") == "error":
                        # Handle error from Retell
                        logger.error(f"Error from Retell: {retell_call_result.get('message')}")
                        error_update = {
                            "call_status": "error",
                            "human_notes": f"Retell error: {retell_call_result.get('message')}"
                        }
                        error_call = await self.call_repository.update_call(db_call["id"], error_update)
                        return error_call
                    
                    # Update the call with Retell information
                    update_data = {
                        "call_status": retell_call_result.get("call_status", "scheduled"),
                        "external_call_id": retell_call_result.get("call_id")
                    }
                    
                    # Update call record
                    updated_call = await self.call_repository.update_call(db_call["id"], update_data)
                    logger.info(f"Triggered call with Retell, call ID: {db_call.get('id')}")
                    return updated_call
                    
                except Exception as e:
                    # Handle any errors
                    logger.error(f"Error triggering call with Retell: {str(e)}")
                    error_update = {
                        "call_status": "error",
                        "human_notes": f"Retell integration error: {str(e)}"
                    }
                    error_call = await self.call_repository.update_call(db_call["id"], error_update)
                    return error_call
            else:
                # No Retell integration available
                update_data = {
                    "call_status": "pending",
                    "human_notes": "Call created without Retell integration. Manual handling required."
                }
                updated_call = await self.call_repository.update_call(db_call["id"], update_data)
                logger.warning(f"Created call with ID: {db_call.get('id')} but no Retell integration available")
                return updated_call
                
        except Exception as e:
            logger.error(f"Error in trigger_call: {str(e)}")
            raise ValueError(f"Failed to trigger call: {str(e)}")
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """
        Get call details by ID with exception handling.
        
        Args:
            call_id: ID of the call
            
        Returns:
            Dictionary containing call details
        
        Raises:
            ValueError: If call not found or other error occurs
        """
        logger.info(f"Getting call with ID: {call_id}")
        try:
            call = await self.call_repository.get_call_by_id(call_id)
            
            if not call:
                logger.warning(f"Call with ID {call_id} not found")
                raise ValueError(f"Call with ID {call_id} not found")
            
            return call
        except Exception as e:
            logger.error(f"Error retrieving call {call_id}: {str(e)}")
            raise ValueError(f"Error retrieving call: {str(e)}")
    
    async def get_calls_by_campaign(self, campaign_id: str,
        page: int = 1,
        page_size: int = 50) -> List[Dict[str, Any]]:
        """
        Get calls for a campaign with exception handling.
        
        Args:
            campaign_id: ID of the campaign
            page: Page number 
            page_size: Page size
            
        Returns:
            List of calls for the campaign
        
        Raises:
            ValueError: If an error occurs during retrieval
        """
        logger.info(f"Getting calls for campaign: {campaign_id}")
        
        try:
            # Get calls using repository
            calls_result = await self.call_repository.get_calls_by_campaign(campaign_id, page, page_size)
            return calls_result.get("calls", [])
        except Exception as e:
            logger.error(f"Error retrieving calls for campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error retrieving calls for campaign: {str(e)}")
    
    async def get_calls_by_lead(self, lead_id: str,
        page: int = 1,
        page_size: int = 50) -> List[Dict[str, Any]]:
        """
        Get calls for a lead with exception handling.
        
        Args:
            lead_id: ID of the lead
            page: Page number
            page_size: Page size
            
        Returns:
            List of calls for the lead
        
        Raises:
            ValueError: If an error occurs during retrieval
        """
        logger.info(f"Getting calls for lead: {lead_id}")
        
        try:
            # Get calls using repository
            calls_result = await self.call_repository.get_calls_by_lead(lead_id, page, page_size)
            return calls_result.get("calls", [])
        except Exception as e:
            logger.error(f"Error retrieving calls for lead {lead_id}: {str(e)}")
            raise ValueError(f"Error retrieving calls for lead: {str(e)}")
    
    async def get_calls_by_date_range(
        self, 
        branch_id: str,  # Renamed from gym_id to branch_id for clarity
        start_date: datetime, 
        end_date: datetime,
        page: int = 1,
        page_size: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get calls for a branch within a date range with exception handling.
        
        Args:
            branch_id: ID of the branch to filter by
            start_date: Start date for the range
            end_date: End date for the range
            page: Page number
            page_size: Page size
            
        Returns:
            List of calls within the date range
        
        Raises:
            ValueError: If an error occurs during retrieval
        """
        logger.info(f"Getting calls for branch {branch_id} from {start_date} to {end_date}")
        
        try:
            # Pass branch_id to the repository function
            calls_result = await self.call_repository.get_calls_by_date_range(
                branch_id, start_date, end_date, page, page_size
            )
            return calls_result.get("calls", [])
        except Exception as e:
            logger.error(f"Error retrieving calls by date range for branch {branch_id}: {str(e)}")
            raise ValueError(f"Error retrieving calls by date range: {str(e)}")

    async def get_scheduled_calls_by_date_range(
        self, 
        branch_id: str,
        start_date: datetime, 
        end_date: datetime,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get scheduled calls within a date range.
        
        Args:
            branch_id: ID of the branch
            start_date: Start date for the range
            end_date: End date for the range
            page: Page number 
            page_size: Page size
            
        Returns:
            Dictionary with calls and pagination info
        """
        logger.info(f"Getting scheduled calls for branch {branch_id} from {start_date} to {end_date}")
        
        try:
            # Use the repository to get scheduled calls
            return await self.call_repository.get_scheduled_calls_by_date_range(
                branch_id, start_date, end_date, page, page_size
            )
        except Exception as e:
            logger.error(f"Error retrieving scheduled calls for branch {branch_id}: {str(e)}")
            return {"calls": [], "total": 0, "page": page, "page_size": page_size}

    async def get_filtered_calls(
        self, 
        branch_id: str,  # Changed from gym_id to branch_id
        page: int = 1,
        page_size: int = 50,
        lead_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        direction: Optional[str] = None,
        outcome: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get filtered calls with all possible combinations of filters at the database level.
        
        Args:
            branch_id: ID of the branch (required for security)
            page: Page number
            page_size: Page size
            lead_id: Optional ID of the lead to filter by
            campaign_id: Optional ID of the campaign to filter by
            direction: Optional call direction to filter by (inbound/outbound)
            outcome: Optional call outcome to filter by
            start_date: Optional start date for date range filtering
            end_date: Optional end date for date range filtering
            
        Returns:
            Dictionary with calls and pagination info
        
        Raises:
            ValueError: If an error occurs during retrieval
        """
        logger.info(f"Getting filtered calls for branch {branch_id} with filters: lead_id={lead_id}, "
                    f"campaign_id={campaign_id}, direction={direction}, outcome={outcome}")
        
        try:
            # Define default date range if not specified
            if not start_date:
                start_date = datetime.now().replace(year=datetime.now().year - 1)
            if not end_date:
                end_date = datetime.now()
            
            # Convert branch_id to UUID if it's a string
            branch_uuid = branch_id if isinstance(branch_id, uuid.UUID) else uuid.UUID(str(branch_id))
            
            # Use the repository's combined filtering method that pushes all filters to the database
            return await self.call_repository.get_calls_with_filters(
                branch_id=branch_uuid,  # Ensure it's a UUID
                page=page,
                page_size=page_size,
                lead_id=lead_id,
                campaign_id=campaign_id,
                direction=direction,
                outcome=outcome,
                start_date=start_date,
                end_date=end_date
            )
                
        except Exception as e:
            logger.error(f"Error retrieving filtered calls: {str(e)}")
            raise ValueError(f"Error retrieving filtered calls: {str(e)}")
    
    async def delete_call(self, call_id: str) -> Dict[str, Any]:
        """
        Delete a call record with exception handling.
        
        Args:
            call_id: ID of the call to delete
            
        Returns:
            Dictionary with status information
            
        Raises:
            ValueError: If call not found or other error occurs
        """
        logger.info(f"Deleting call with ID: {call_id}")
        
        try:
            # First verify the call exists
            call = await self.call_repository.get_call_by_id(call_id)
            
            if not call:
                logger.warning(f"Call with ID {call_id} not found")
                raise ValueError(f"Call with ID {call_id} not found")
            
            # Delete the call
            result = await self.call_repository.delete_call(call_id)
            
            if not result:
                logger.warning(f"Failed to delete call with ID {call_id}")
                raise ValueError(f"Failed to delete call with ID {call_id}")
            
            logger.info(f"Successfully deleted call with ID: {call_id}")
            return {"status": "success", "message": f"Call with ID {call_id} deleted successfully"}
        except ValueError as ve:
            # Re-raise the value errors with proper message
            raise ve
        except Exception as e:
            # Convert other exceptions to ValueError
            logger.error(f"Error deleting call {call_id}: {str(e)}")
            raise ValueError(f"Error deleting call: {str(e)}")

    async def process_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a webhook event from the call provider.
        
        Args:
            event_data: Dictionary containing event data
            
        Returns:
            Dictionary containing the processed event result
        """
        logger.info(f"Processing webhook event: {event_data.get('event_type') or event_data.get('event')}")
        
        # If we have the Retell integration and this is a Retell webhook, process it
        if self.retell_integration and event_data.get("source") == "retell":
            try:
                # Process the webhook using the Retell integration
                processed_webhook = await self.retell_integration.process_webhook(event_data)
                
                # Get the mapped event type and call ID
                event_type = processed_webhook.get("event_type")
                external_call_id = processed_webhook.get("call_id")
                
                if not external_call_id:
                    logger.warning("No call ID provided in webhook event")
                    return {
                        "status": "error",
                        "message": "No call ID provided in webhook event",
                        "processed_webhook": processed_webhook
                    }
                
                # Find our internal call with this external call ID
                call = await self.call_repository.get_call_by_external_id(external_call_id)
                
                if not call:
                    logger.warning(f"Call with external ID {external_call_id} not found")
                    return {
                        "status": "error",
                        "message": f"Call with external ID {external_call_id} not found",
                        "processed_webhook": processed_webhook
                    }
                
                call_id = call.get("id")
                
                # Process the event based on type
                if event_type == "call.started":
                    # Update call status to in_progress
                    update_data = {
                        "call_status": "in_progress",
                        "start_time": datetime.fromtimestamp(processed_webhook.get("timestamp", 0) / 1000) if processed_webhook.get("timestamp") else datetime.now()
                    }
                    updated_call = await self.call_repository.update_call(call_id, update_data)
                    return {"status": "success", "call": updated_call}
                
                elif event_type == "call.ended":
                    # Update call with transcript, recording, and status
                    transcript = processed_webhook.get("transcript")
                    recording_url = processed_webhook.get("recording_url")
                    duration = processed_webhook.get("duration", 0)
                    
                    # Update call record
                    update_data = {
                        "call_status": "completed",
                        "end_time": datetime.fromtimestamp(processed_webhook.get("timestamp", 0) / 1000) if processed_webhook.get("timestamp") else datetime.now(),
                        "duration": duration,
                        "recording_url": recording_url,
                        "transcript": transcript
                    }
                    updated_call = await self.call_repository.update_call(call_id, update_data)
                    
                    # If this call is associated with a campaign, increment the campaign's call count
                    if campaign_id := updated_call.get("campaign_id"):
                        try:
                            from ...services.campaign.factory import create_campaign_service
                            campaign_service = create_campaign_service()
                            await campaign_service.increment_call_count(campaign_id)
                            logger.info(f"Incremented call count for campaign {campaign_id}")
                        except Exception as e:
                            logger.error(f"Failed to increment campaign call count: {str(e)}")
                    
                    return {"status": "success", "call": updated_call}
                
                elif event_type == "call.analyzed":
                    # Update call with analysis data
                    summary = processed_webhook.get("summary")
                    sentiment = processed_webhook.get("sentiment")
                    
                    update_data = {
                        "summary": summary,
                        "sentiment": sentiment
                    }
                    
                    updated_call = await self.call_repository.update_call(call_id, update_data)
                    return {"status": "success", "call": updated_call}
                
                else:
                    logger.warning(f"Unknown event type from Retell: {event_type}")
                    return {"status": "error", "message": f"Unknown event type: {event_type}"}
                
            except Exception as e:
                logger.error(f"Error processing Retell webhook: {str(e)}")
                return {"status": "error", "message": str(e)}
        
        # Regular webhook processing (non-Retell or fallback)
        event_type = event_data.get("event_type")
        call_id = event_data.get("call_id")
        
        if not call_id:
            logger.warning("No call ID provided in webhook event")
            raise ValueError("No call ID provided in webhook event")
        
        # Get call
        call = await self.call_repository.get_call_by_id(call_id)
        
        if not call:
            logger.warning(f"Call with ID {call_id} not found")
            raise ValueError(f"Call with ID {call_id} not found")
        
        # Process event based on type
        if event_type == "call.started":
            # Update call status to in_progress
            update_data = {
                "call_status": "in_progress",
                "start_time": datetime.now()
            }
            updated_call = await self.call_repository.update_call(call_id, update_data)
            return {"status": "success", "call": updated_call}
        
        elif event_type == "call.ended":
            # Update call status to completed
            duration = event_data.get("duration", 0)
            update_data = {
                "call_status": "completed",
                "end_time": datetime.now(),
                "duration": duration
            }
            updated_call = await self.call_repository.update_call(call_id, update_data)
            
            # If this call is associated with a campaign, increment the campaign's call count
            if campaign_id := updated_call.get("campaign_id"):
                try:
                    from ...services.campaign.factory import create_campaign_service
                    campaign_service = create_campaign_service()
                    await campaign_service.increment_call_count(campaign_id)
                    logger.info(f"Incremented call count for campaign {campaign_id}")
                except Exception as e:
                    logger.error(f"Failed to increment campaign call count: {str(e)}")
            
            return {"status": "success", "call": updated_call}
        
        elif event_type == "call.recording":
            # Update call recording
            recording_url = event_data.get("recording_url")
            if not recording_url:
                logger.warning("No recording URL provided in webhook event")
                raise ValueError("No recording URL provided in webhook event")
            
            updated_call = await self.call_repository.update_call(call_id, {"recording_url": recording_url})
            return {"status": "success", "call": updated_call}
        
        elif event_type == "call.transcript":
            # Update call transcript
            transcript = event_data.get("transcript")
            if not transcript:
                logger.warning("No transcript provided in webhook event")
                raise ValueError("No transcript provided in webhook event")
            
            updated_call = await self.call_repository.update_call(call_id, {"transcript": transcript})
            return {"status": "success", "call": updated_call}
        
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return {"status": "error", "message": f"Unknown event type: {event_type}"}
    
    #Optional.
    async def create_follow_up_call(self, follow_up_call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a follow-up call.
        
        Args:
            follow_up_call_data: Dictionary containing follow-up call details
            
        Returns:
            Dictionary containing the created follow-up call data
        """
        logger.info(f"Creating follow-up call with data: {follow_up_call_data}")
        
        # Set default values if not provided
        if "call_status" not in follow_up_call_data:
            follow_up_call_data["call_status"] = "scheduled"
        
        if "created_at" not in follow_up_call_data:
            follow_up_call_data["created_at"] = datetime.now()
        
        # Create follow-up call using repository
        follow_up_call = await self.call_repository.create_follow_up_call(follow_up_call_data)
        
        logger.info(f"Created follow-up call with ID: {follow_up_call.get('id')}")
        return follow_up_call
    
    #Optional. 
    async def get_follow_up_call(self, follow_up_call_id: str) -> Dict[str, Any]:
        """
        Get follow-up call details by ID.
        
        Args:
            follow_up_call_id: ID of the follow-up call
            
        Returns:
            Dictionary containing follow-up call details
        """
        logger.info(f"Getting follow-up call with ID: {follow_up_call_id}")
        follow_up_call = await self.call_repository.get_follow_up_call_by_id(follow_up_call_id)
        
        if not follow_up_call:
            logger.warning(f"Follow-up call with ID {follow_up_call_id} not found")
            raise ValueError(f"Follow-up call with ID {follow_up_call_id} not found")
        
        return follow_up_call
    
    #Optional.
    async def update_follow_up_call(self, follow_up_call_id: str, follow_up_call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update follow-up call information.
        
        Args:
            follow_up_call_id: ID of the follow-up call
            follow_up_call_data: Dictionary containing updated follow-up call information
            
        Returns:
            Dictionary containing the updated follow-up call details
        """
        logger.info(f"Updating follow-up call with ID: {follow_up_call_id} with data: {follow_up_call_data}")
        
        # Update follow-up call using repository
        updated_follow_up_call = await self.call_repository.update_follow_up_call(follow_up_call_id, follow_up_call_data)
        
        if not updated_follow_up_call:
            logger.warning(f"Follow-up call with ID {follow_up_call_id} not found")
            raise ValueError(f"Follow-up call with ID {follow_up_call_id} not found")
        
        logger.info(f"Updated follow-up call with ID: {follow_up_call_id}")
        return updated_follow_up_call
    
    #Optional. 
    async def delete_follow_up_call(self, follow_up_call_id: str) -> bool:
        """
        Delete a follow-up call.
        
        Args:
            follow_up_call_id: ID of the follow-up call
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Deleting follow-up call with ID: {follow_up_call_id}")
        
        # Delete follow-up call using repository
        result = await self.call_repository.delete_follow_up_call(follow_up_call_id)
        
        if not result:
            logger.warning(f"Follow-up call with ID {follow_up_call_id} not found")
            raise ValueError(f"Follow-up call with ID {follow_up_call_id} not found")
        
        logger.info(f"Deleted follow-up call with ID: {follow_up_call_id}")
        return True
    
    #Optional.
    async def get_follow_up_calls_by_campaign(self, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Get follow-up calls for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            List of follow-up calls for the campaign
        """
        logger.info(f"Getting follow-up calls for campaign: {campaign_id}")
        
        # Get follow-up calls using repository
        follow_up_calls_result = await self.call_repository.get_follow_up_calls_by_campaign(campaign_id)
        
        return follow_up_calls_result.get("follow_up_calls", [])
    
    #Optional.
    async def get_follow_up_calls_by_lead(self, lead_id: str) -> List[Dict[str, Any]]:
        """
        Get follow-up calls for a lead.
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            List of follow-up calls for the lead
        """
        logger.info(f"Getting follow-up calls for lead: {lead_id}")
        
        # Get follow-up calls using repository
        follow_up_calls_result = await self.call_repository.get_follow_up_calls_by_lead(lead_id)
        
        return follow_up_calls_result.get("follow_up_calls", [])
     
    async def update_call(self, call_id: str, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update call information with exception handling.
        
        Args:
            call_id: ID of the call
            call_data: Dictionary containing updated call information
            
        Returns:
            Dictionary containing the updated call details
            
        Raises:
            ValueError: If call not found or other error occurs
        """
        logger.info(f"Updating call with ID: {call_id} with data: {call_data}")
        
        try:
            # Update call using repository
            updated_call = await self.call_repository.update_call(call_id, call_data)
            
            if not updated_call:
                logger.warning(f"Call with ID {call_id} not found")
                raise ValueError(f"Call with ID {call_id} not found")
            
            logger.info(f"Updated call with ID: {call_id}")
            return updated_call
        except Exception as e:
            logger.error(f"Error updating call {call_id}: {str(e)}")
            raise ValueError(f"Error updating call: {str(e)}")
    
    #Optional.
    async def process_call_recording(self, call_id: str, recording_url: str) -> Dict[str, Any]:
        """
        Process a call recording.
        
        Args:
            call_id: ID of the call
            recording_url: URL of the recording
            
        Returns:
            Dictionary containing processed call details
        """
        logger.info(f"Processing recording for call: {call_id}")
        
        # Check if this should be run as a background task
        if recording_url and isinstance(recording_url, dict) and recording_url.get("use_background_task", False):
            # Get the actual URL
            actual_url = recording_url.get("url", "")
            
            # Import here to avoid circular imports
            from ...tasks.call.task_definitions import process_call_recording as process_recording_task
            
            # Queue the task for background processing
            process_recording_task.delay(call_id, actual_url)
            
            # Return minimal information immediately
            return {"id": call_id, "status": "recording_processing_queued"}
        
        # Otherwise, process recording synchronously
        # Handle the case where recording_url might be a dict from above logic
        actual_url = recording_url.get("url", "") if isinstance(recording_url, dict) else recording_url
        
        # Update call recording using repository
        updated_call = await self.call_repository.update_call_recording(call_id, actual_url)
        
        if not updated_call:
            logger.warning(f"Call with ID {call_id} not found")
            raise ValueError(f"Call with ID {call_id} not found")
        
        logger.info(f"Processed recording for call with ID: {call_id}")
        return updated_call
    
    #Optional.
    async def generate_call_summary(self, call_id: str, transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary from a call transcript.
        
        Args:
            call_id: ID of the call
            transcript: List of transcript entries
            
        Returns:
            Dictionary containing the summary and other analysis results
        """
        logger.info(f"Generating summary for call: {call_id}")
        
        # Check if this should be run as a background task
        if transcript and isinstance(transcript, dict) and transcript.get("use_background_task", False):
            # Get the actual transcript
            actual_transcript = transcript.get("entries", [])
            
            # Import here to avoid circular imports
            from ...tasks.call.task_definitions import analyze_call_transcript as analyze_transcript_task
            
            # Queue the task for background processing
            analyze_transcript_task.delay(call_id)
            
            # Return minimal information immediately
            return {"id": call_id, "status": "summary_generation_queued"}
        
        # Otherwise, process transcript synchronously
        # Convert transcript list to string for storage
        if isinstance(transcript, dict):
            transcript_entries = transcript.get("entries", [])
        else:
            transcript_entries = transcript
            
        transcript_text = "\n".join([f"{entry.get('speaker', 'Unknown')}: {entry.get('text', '')}" for entry in transcript_entries])
        
        # Update call transcript using repository
        updated_call = await self.call_repository.update_call_transcript(call_id, transcript_text)
        
        if not updated_call:
            logger.warning(f"Call with ID {call_id} not found")
            raise ValueError(f"Call with ID {call_id} not found")
        
        # Generate summary (placeholder implementation)
        # In a real implementation, you would use NLP to generate a summary
        summary = "This is a placeholder summary of the call."
        sentiment = "neutral"
        
        # Update call metrics with summary and sentiment
        metrics_data = {
            "summary": summary,
            "sentiment": sentiment
        }
        
        updated_call = await self.call_repository.update_call_metrics(call_id, metrics_data)
        
        logger.info(f"Generated summary for call with ID: {call_id}")
        return updated_call
