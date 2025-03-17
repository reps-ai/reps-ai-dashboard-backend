"""
Service for managing calls using voice agent providers.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..db.repositories.call import CallRepository
from ..db.repositories.lead import LeadRepository
from ..integrations.voice_agent import VoiceAgentFactory, VoiceAgentProvider
from ..utils.logging.logger import get_logger

logger = get_logger(__name__)

class CallService:
    """
    Service for managing calls using voice agent providers.
    """
    
    def __init__(
        self,
        call_repository: CallRepository,
        lead_repository: LeadRepository,
        voice_agent_provider: Optional[VoiceAgentProvider] = None,
        voice_agent_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the call service.

        Args:
            call_repository: Repository for call operations
            lead_repository: Repository for lead operations
            voice_agent_provider: Optional pre-initialized voice agent provider
            voice_agent_config: Configuration for creating a voice agent provider if not provided
        """
        self.call_repository = call_repository
        self.lead_repository = lead_repository
        self.voice_agent_provider = voice_agent_provider
        self.voice_agent_config = voice_agent_config or {}
    
    async def initialize_provider(self, provider_type: str = "retell") -> None:
        """
        Initialize the voice agent provider if not already initialized.

        Args:
            provider_type: Type of provider to create
        """
        if not self.voice_agent_provider:
            if not self.voice_agent_config:
                raise ValueError("Voice agent configuration is required")
            
            self.voice_agent_provider = await VoiceAgentFactory.create_provider(
                provider_type, self.voice_agent_config
            )
    
    async def create_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new call.

        Args:
            call_data: Dictionary containing call details including:
                - lead_id: ID of the lead being called
                - phone_number: Phone number to call
                - campaign_id: ID of the campaign this call belongs to
                - agent_config: Configuration for the voice agent

        Returns:
            Dictionary containing call details
        """
        # Ensure provider is initialized
        if not self.voice_agent_provider:
            await self.initialize_provider()
        
        # Validate lead exists
        lead_id = call_data.get("lead_id")
        lead = await self.lead_repository.get_lead_by_id(lead_id)
        if not lead:
            raise ValueError(f"Lead not found: {lead_id}")
        
        # Create call with provider
        provider_call = await self.voice_agent_provider.create_call(call_data)
        
        # Store call in database
        db_call_data = {
            "lead_id": lead_id,
            "campaign_id": call_data.get("campaign_id"),
            "gym_id": call_data.get("gym_id"),
            "provider": self.voice_agent_config.get("provider_type", "retell"),
            "provider_call_id": provider_call.get("provider_call_id"),
            "status": provider_call.get("status"),
            "created_at": datetime.now().isoformat(),
            "provider_data": provider_call.get("provider_data", {})
        }
        
        # Create call record in database
        call = await self.call_repository.create_call(db_call_data)
        
        return call
    
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """
        End an active call.

        Args:
            call_id: ID of the call to end

        Returns:
            Dictionary containing updated call details
        """
        # Ensure provider is initialized
        if not self.voice_agent_provider:
            await self.initialize_provider()
        
        # Get call from database
        call = await self.call_repository.get_call_by_id(call_id)
        if not call:
            raise ValueError(f"Call not found: {call_id}")
        
        # End call with provider
        provider_call_id = call.get("provider_call_id")
        provider_result = await self.voice_agent_provider.end_call(provider_call_id)
        
        # Update call in database
        update_data = {
            "status": provider_result.get("status"),
            "duration": provider_result.get("duration"),
            "ended_at": datetime.now().isoformat(),
            "provider_data": provider_result.get("provider_data", {})
        }
        
        updated_call = await self.call_repository.update_call(call_id, update_data)
        
        return updated_call
    
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """
        Get the current status of a call.

        Args:
            call_id: ID of the call

        Returns:
            Dictionary containing call status details
        """
        # Ensure provider is initialized
        if not self.voice_agent_provider:
            await self.initialize_provider()
        
        # Get call from database
        call = await self.call_repository.get_call_by_id(call_id)
        if not call:
            raise ValueError(f"Call not found: {call_id}")
        
        # Get status from provider
        provider_call_id = call.get("provider_call_id")
        provider_status = await self.voice_agent_provider.get_call_status(provider_call_id)
        
        # Update call in database if status has changed
        if provider_status.get("status") != call.get("status"):
            update_data = {
                "status": provider_status.get("status"),
                "duration": provider_status.get("duration"),
                "provider_data": provider_status.get("provider_data", {})
            }
            
            if provider_status.get("status") in ["completed", "failed", "canceled"]:
                update_data["ended_at"] = datetime.now().isoformat()
            
            await self.call_repository.update_call(call_id, update_data)
        
        return provider_status
    
    async def get_call_recording(self, call_id: str) -> Dict[str, Any]:
        """
        Get the recording for a completed call.

        Args:
            call_id: ID of the call

        Returns:
            Dictionary containing recording details
        """
        # Ensure provider is initialized
        if not self.voice_agent_provider:
            await self.initialize_provider()
        
        # Get call from database
        call = await self.call_repository.get_call_by_id(call_id)
        if not call:
            raise ValueError(f"Call not found: {call_id}")
        
        # Get recording from provider
        provider_call_id = call.get("provider_call_id")
        recording = await self.voice_agent_provider.get_call_recording(provider_call_id)
        
        # Save recording info to database
        await self.call_repository.save_call_recording(call_id, recording)
        
        return recording
    
    async def get_call_transcript(self, call_id: str) -> List[Dict[str, Any]]:
        """
        Get the transcript for a completed call.

        Args:
            call_id: ID of the call

        Returns:
            List of transcript segments
        """
        # Ensure provider is initialized
        if not self.voice_agent_provider:
            await self.initialize_provider()
        
        # Get call from database
        call = await self.call_repository.get_call_by_id(call_id)
        if not call:
            raise ValueError(f"Call not found: {call_id}")
        
        # Get transcript from provider
        provider_call_id = call.get("provider_call_id")
        transcript = await self.voice_agent_provider.get_call_transcript(provider_call_id)
        
        # Save transcript to database
        await self.call_repository.save_call_transcript(call_id, transcript)
        
        return transcript
    
    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a webhook from the voice agent provider.

        Args:
            webhook_data: Dictionary containing webhook data

        Returns:
            Dictionary containing processed webhook data
        """
        # Ensure provider is initialized
        if not self.voice_agent_provider:
            await self.initialize_provider()
        
        # Validate webhook
        is_valid = await self.voice_agent_provider.validate_webhook(webhook_data)
        if not is_valid:
            raise ValueError("Invalid webhook signature")
        
        # Parse webhook
        parsed_webhook = await self.voice_agent_provider.parse_webhook(webhook_data)
        
        # Process webhook based on event type
        event_type = parsed_webhook.get("event_type")
        provider_call_id = parsed_webhook.get("provider_call_id")
        
        # Find the call in our database
        calls = await self.call_repository.get_calls_by_provider_id(provider_call_id)
        if not calls or len(calls) == 0:
            logger.warning(f"Call not found for provider call ID: {provider_call_id}")
            return parsed_webhook
        
        call = calls[0]
        call_id = call.get("id")
        
        # Update call based on event type
        if event_type == "call_started":
            await self.call_repository.update_call_status(call_id, "in_progress")
        elif event_type == "call_ended":
            await self.call_repository.update_call_status(call_id, "completed")
            
            # Update call duration if available
            if "duration" in parsed_webhook:
                await self.call_repository.update_call_metrics(call_id, {
                    "duration": parsed_webhook.get("duration")
                })
        elif event_type == "call_failed":
            await self.call_repository.update_call_status(call_id, "failed")
        elif event_type == "recording_available":
            # Save recording URL
            if "recording_url" in parsed_webhook:
                await self.call_repository.save_call_recording(call_id, {
                    "recording_url": parsed_webhook.get("recording_url")
                })
        elif event_type == "transcript_available":
            # Fetch and save transcript
            transcript = await self.voice_agent_provider.get_call_transcript(provider_call_id)
            await self.call_repository.save_call_transcript(call_id, transcript)
        
        return parsed_webhook 