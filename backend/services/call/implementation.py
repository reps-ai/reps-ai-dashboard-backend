"""
Implementation of the Call Management Service.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from .interface import CallService
from ...db.repositories.call import CallRepository
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

class DefaultCallService(CallService):
    """
    Default implementation of the Call Management Service.
    """
    
    def __init__(self, call_repository: CallRepository):
        """
        Initialize the call service.
        
        Args:
            call_repository: Repository for call operations
        """
        self.call_repository = call_repository
    
    async def trigger_call(self, lead_id: str, campaign_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger a call to a lead.
        
        Args:
            lead_id: ID of the lead to call
            campaign_id: Optional ID of the campaign
            
        Returns:
            Dictionary containing call details
        """
        logger.info(f"Triggering call to lead: {lead_id}")
        
        # Create call data
        call_data = {
            "lead_id": lead_id,
            "call_status": "scheduled",
            "call_type": "outbound",
            "created_at": datetime.now(),
            "start_time": datetime.now()
        }
        
        if campaign_id:
            call_data["campaign_id"] = campaign_id
        
        # Create call using repository
        call = await self.call_repository.create_call(call_data)
        
        logger.info(f"Triggered call with ID: {call.get('id')}")
        return call
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """
        Get call details by ID.
        
        Args:
            call_id: ID of the call
            
        Returns:
            Dictionary containing call details
        """
        logger.info(f"Getting call with ID: {call_id}")
        call = await self.call_repository.get_call_by_id(call_id)
        
        if not call:
            logger.warning(f"Call with ID {call_id} not found")
            raise ValueError(f"Call with ID {call_id} not found")
        
        return call
      
    async def get_calls_by_campaign(self, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Get calls for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            List of calls for the campaign
        """
        logger.info(f"Getting calls for campaign: {campaign_id}")
        
        # Get calls using repository
        calls_result = await self.call_repository.get_calls_by_campaign(campaign_id)
        
        return calls_result.get("calls", [])
    
    async def get_calls_by_lead(self, lead_id: str) -> List[Dict[str, Any]]:
        """
        Get calls for a lead.
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            List of calls for the lead
        """
        logger.info(f"Getting calls for lead: {lead_id}")
        
        # Get calls using repository
        calls_result = await self.call_repository.get_calls_by_lead(lead_id)
        
        return calls_result.get("calls", [])
    
    async def get_calls_by_date_range(
        self, 
        gym_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get calls for a gym within a date range.
        
        Args:
            gym_id: ID of the gym
            start_date: Start date for the range
            end_date: End date for the range
            
        Returns:
            List of calls within the date range
        """
        logger.info(f"Getting calls for gym {gym_id} from {start_date} to {end_date}")
        
        # Get calls using repository
        calls_result = await self.call_repository.get_calls_by_date_range(
            gym_id, start_date, end_date
        )
        
        return calls_result.get("calls", [])
    
    async def process_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a webhook event from the call provider.
        
        Args:
            event_data: Dictionary containing event data
            
        Returns:
            Dictionary containing the processed event result
        """
        logger.info(f"Processing webhook event: {event_data.get('event_type')}")
        
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
            return {"status": "success", "call": updated_call}
        
        elif event_type == "call.recording":
            # Update call recording
            recording_url = event_data.get("recording_url")
            if not recording_url:
                logger.warning("No recording URL provided in webhook event")
                raise ValueError("No recording URL provided in webhook event")
            
            updated_call = await self.call_repository.update_call_recording(call_id, recording_url)
            return {"status": "success", "call": updated_call}
        
        elif event_type == "call.transcript":
            # Update call transcript
            transcript = event_data.get("transcript")
            if not transcript:
                logger.warning("No transcript provided in webhook event")
                raise ValueError("No transcript provided in webhook event")
            
            updated_call = await self.call_repository.update_call_transcript(call_id, transcript)
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
    

    #Optional. 
    async def update_call(self, call_id: str, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update call information.
        
        Args:
            call_id: ID of the call
            call_data: Dictionary containing updated call information
            
        Returns:
            Dictionary containing the updated call details
        """
        logger.info(f"Updating call with ID: {call_id} with data: {call_data}")
        
        # Update call using repository
        updated_call = await self.call_repository.update_call(call_id, call_data)
        
        if not updated_call:
            logger.warning(f"Call with ID {call_id} not found")
            raise ValueError(f"Call with ID {call_id} not found")
        
        logger.info(f"Updated call with ID: {call_id}")
        return updated_call
    

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
        
        # Update call recording using repository
        updated_call = await self.call_repository.update_call_recording(call_id, recording_url)
        
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
        
        # Convert transcript list to string for storage
        transcript_text = "\n".join([f"{entry.get('speaker', 'Unknown')}: {entry.get('text', '')}" for entry in transcript])
        
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
  