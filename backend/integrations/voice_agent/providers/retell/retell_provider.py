"""
Retell implementation of the voice agent provider interface.
"""
import json
import hmac
import hashlib
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime

from ....voice_agent.voice_agent_provider import VoiceAgentProvider
from .....utils.logging.logger import get_logger

logger = get_logger(__name__)

class RetellVoiceAgentProvider(VoiceAgentProvider):
    """
    Retell implementation of the voice agent provider interface.
    """
    
    def __init__(self):
        """Initialize the Retell provider."""
        self.api_key = None
        self.api_base_url = "https://api.retellai.com/v1"
        self.webhook_secret = None
        self.session = None
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the Retell provider with configuration.

        Args:
            config: Dictionary containing Retell-specific configuration:
                - api_key: Retell API key
                - webhook_secret: Secret for validating webhooks
                - api_base_url: Optional custom API base URL
        """
        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ValueError("Retell API key is required")
        
        self.webhook_secret = config.get("webhook_secret")
        if not self.webhook_secret:
            raise ValueError("Retell webhook secret is required")
        
        if custom_url := config.get("api_base_url"):
            self.api_base_url = custom_url
        
        # Create aiohttp session for API calls
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        logger.info("Retell voice agent provider initialized")
    
    async def __del__(self):
        """Clean up resources when the provider is destroyed."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def create_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new call with Retell.

        Args:
            call_data: Dictionary containing call details including:
                - lead_id: ID of the lead being called
                - phone_number: Phone number to call
                - campaign_id: ID of the campaign this call belongs to
                - agent_config: Configuration for the voice agent

        Returns:
            Dictionary containing Retell-specific call details
        """
        if not self.session:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        
        phone_number = call_data.get("phone_number")
        if not phone_number:
            raise ValueError("Phone number is required")
        
        agent_config = call_data.get("agent_config", {})
        
        # Prepare Retell-specific payload
        payload = {
            "phoneNumber": phone_number,
            "llmConfig": {
                "llmModel": agent_config.get("llm_model", "gpt-4"),
                "systemPrompt": agent_config.get("system_prompt", ""),
                "temperature": agent_config.get("temperature", 0.7),
            },
            "voiceConfig": {
                "voiceId": agent_config.get("voice_id", "eleven_labs_josh"),
                "speed": agent_config.get("voice_speed", 1.0),
            },
            "webhookUrl": agent_config.get("webhook_url", ""),
            "metadata": {
                "lead_id": call_data.get("lead_id", ""),
                "campaign_id": call_data.get("campaign_id", ""),
                "gym_id": call_data.get("gym_id", ""),
            }
        }
        
        try:
            async with self.session.post(
                f"{self.api_base_url}/calls", 
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to create Retell call: {error_text}")
                    raise RuntimeError(f"Failed to create Retell call: {error_text}")
                
                result = await response.json()
                
                return {
                    "provider_call_id": result.get("id"),
                    "status": result.get("status"),
                    "provider_data": result
                }
        except aiohttp.ClientError as e:
            logger.error(f"Error creating Retell call: {str(e)}")
            raise RuntimeError(f"Error creating Retell call: {str(e)}")
    
    async def end_call(self, provider_call_id: str) -> Dict[str, Any]:
        """
        End an active Retell call.

        Args:
            provider_call_id: Retell's unique identifier for the call

        Returns:
            Dictionary containing call outcome details
        """
        if not self.session:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        
        try:
            async with self.session.post(
                f"{self.api_base_url}/calls/{provider_call_id}/end"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to end Retell call: {error_text}")
                    raise RuntimeError(f"Failed to end Retell call: {error_text}")
                
                result = await response.json()
                
                return {
                    "status": result.get("status"),
                    "duration": result.get("duration"),
                    "provider_data": result
                }
        except aiohttp.ClientError as e:
            logger.error(f"Error ending Retell call: {str(e)}")
            raise RuntimeError(f"Error ending Retell call: {str(e)}")
    
    async def get_call_status(self, provider_call_id: str) -> Dict[str, Any]:
        """
        Get the current status of a Retell call.

        Args:
            provider_call_id: Retell's unique identifier for the call

        Returns:
            Dictionary containing call status details
        """
        if not self.session:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        
        try:
            async with self.session.get(
                f"{self.api_base_url}/calls/{provider_call_id}"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to get Retell call status: {error_text}")
                    raise RuntimeError(f"Failed to get Retell call status: {error_text}")
                
                result = await response.json()
                
                # Map Retell status to standardized status
                status_mapping = {
                    "queued": "queued",
                    "in_progress": "in_progress",
                    "completed": "completed",
                    "failed": "failed",
                    "canceled": "canceled"
                }
                
                return {
                    "status": status_mapping.get(result.get("status"), "unknown"),
                    "duration": result.get("duration"),
                    "start_time": result.get("startTime"),
                    "end_time": result.get("endTime"),
                    "provider_data": result
                }
        except aiohttp.ClientError as e:
            logger.error(f"Error getting Retell call status: {str(e)}")
            raise RuntimeError(f"Error getting Retell call status: {str(e)}")
    
    async def get_call_recording(self, provider_call_id: str) -> Dict[str, Any]:
        """
        Get the recording for a completed Retell call.

        Args:
            provider_call_id: Retell's unique identifier for the call

        Returns:
            Dictionary containing recording details
        """
        if not self.session:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        
        try:
            async with self.session.get(
                f"{self.api_base_url}/calls/{provider_call_id}/recording"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to get Retell call recording: {error_text}")
                    raise RuntimeError(f"Failed to get Retell call recording: {error_text}")
                
                result = await response.json()
                
                return {
                    "recording_url": result.get("url"),
                    "duration": result.get("duration"),
                    "format": "mp3",  # Retell typically provides MP3 recordings
                    "provider_data": result
                }
        except aiohttp.ClientError as e:
            logger.error(f"Error getting Retell call recording: {str(e)}")
            raise RuntimeError(f"Error getting Retell call recording: {str(e)}")
    
    async def get_call_transcript(self, provider_call_id: str) -> List[Dict[str, Any]]:
        """
        Get the transcript for a completed Retell call.

        Args:
            provider_call_id: Retell's unique identifier for the call

        Returns:
            List of transcript segments
        """
        if not self.session:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        
        try:
            async with self.session.get(
                f"{self.api_base_url}/calls/{provider_call_id}/transcript"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to get Retell call transcript: {error_text}")
                    raise RuntimeError(f"Failed to get Retell call transcript: {error_text}")
                
                result = await response.json()
                transcript_segments = result.get("transcript", [])
                
                # Transform Retell transcript format to standardized format
                standardized_transcript = []
                for segment in transcript_segments:
                    standardized_transcript.append({
                        "speaker": "agent" if segment.get("role") == "assistant" else "user",
                        "text": segment.get("text", ""),
                        "start_time": segment.get("startTime", 0),
                        "end_time": segment.get("endTime", 0)
                    })
                
                return standardized_transcript
        except aiohttp.ClientError as e:
            logger.error(f"Error getting Retell call transcript: {str(e)}")
            raise RuntimeError(f"Error getting Retell call transcript: {str(e)}")
    
    async def stream_call_audio(self, provider_call_id: str) -> AsyncGenerator[bytes, None]:
        """
        Stream the audio of an active Retell call.

        Args:
            provider_call_id: Retell's unique identifier for the call

        Yields:
            Audio chunks as bytes
        """
        if not self.session:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        
        try:
            async with self.session.get(
                f"{self.api_base_url}/calls/{provider_call_id}/stream",
                headers={"Accept": "audio/mpeg"}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to stream Retell call audio: {error_text}")
                    raise RuntimeError(f"Failed to stream Retell call audio: {error_text}")
                
                # Stream the audio chunks
                async for chunk in response.content.iter_chunked(1024):
                    yield chunk
        except aiohttp.ClientError as e:
            logger.error(f"Error streaming Retell call audio: {str(e)}")
            raise RuntimeError(f"Error streaming Retell call audio: {str(e)}")
    
    async def update_agent_config(self, provider_call_id: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the configuration of an active Retell voice agent.

        Args:
            provider_call_id: Retell's unique identifier for the call
            agent_config: New configuration for the voice agent

        Returns:
            Dictionary containing updated agent details
        """
        if not self.session:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        
        # Prepare Retell-specific payload
        payload = {}
        
        if "system_prompt" in agent_config:
            payload["llmConfig"] = {
                "systemPrompt": agent_config["system_prompt"]
            }
            
            if "llm_model" in agent_config:
                payload["llmConfig"]["llmModel"] = agent_config["llm_model"]
                
            if "temperature" in agent_config:
                payload["llmConfig"]["temperature"] = agent_config["temperature"]
        
        if "voice_id" in agent_config:
            payload["voiceConfig"] = {
                "voiceId": agent_config["voice_id"]
            }
            
            if "voice_speed" in agent_config:
                payload["voiceConfig"]["speed"] = agent_config["voice_speed"]
        
        if not payload:
            logger.warning("No valid configuration updates provided")
            return {"status": "unchanged"}
        
        try:
            async with self.session.patch(
                f"{self.api_base_url}/calls/{provider_call_id}",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to update Retell agent config: {error_text}")
                    raise RuntimeError(f"Failed to update Retell agent config: {error_text}")
                
                result = await response.json()
                
                return {
                    "status": "updated",
                    "provider_data": result
                }
        except aiohttp.ClientError as e:
            logger.error(f"Error updating Retell agent config: {str(e)}")
            raise RuntimeError(f"Error updating Retell agent config: {str(e)}")
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get a list of available voice options from Retell.

        Returns:
            List of voice options
        """
        if not self.session:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        
        try:
            async with self.session.get(
                f"{self.api_base_url}/voices"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to get Retell voices: {error_text}")
                    raise RuntimeError(f"Failed to get Retell voices: {error_text}")
                
                result = await response.json()
                voices = result.get("voices", [])
                
                # Transform Retell voice format to standardized format
                standardized_voices = []
                for voice in voices:
                    standardized_voices.append({
                        "voice_id": voice.get("id"),
                        "name": voice.get("name"),
                        "gender": voice.get("gender", "unknown"),
                        "language": voice.get("language", "en"),
                        "provider": "retell",
                        "provider_data": voice
                    })
                
                return standardized_voices
        except aiohttp.ClientError as e:
            logger.error(f"Error getting Retell voices: {str(e)}")
            raise RuntimeError(f"Error getting Retell voices: {str(e)}")
    
    async def validate_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Validate that a webhook request is authentic and from Retell.

        Args:
            webhook_data: Dictionary containing webhook request data including:
                - headers: HTTP headers from the request
                - body: Raw body of the request

        Returns:
            True if the webhook is valid, False otherwise
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, skipping validation")
            return True
        
        headers = webhook_data.get("headers", {})
        body = webhook_data.get("body", "")
        
        signature = headers.get("retell-signature")
        if not signature:
            logger.warning("No Retell signature in webhook headers")
            return False
        
        # Compute HMAC using webhook secret
        computed_signature = hmac.new(
            self.webhook_secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(computed_signature, signature)
    
    async def parse_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a webhook request from Retell.

        Args:
            webhook_data: Dictionary containing webhook request data

        Returns:
            Dictionary containing parsed webhook data in a standardized format
        """
        body = webhook_data.get("body", "{}")
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                logger.error("Failed to parse webhook body as JSON")
                return {"event_type": "unknown"}
        
        event_type = body.get("type")
        call_id = body.get("callId")
        
        # Map Retell event types to standardized event types
        event_mapping = {
            "call.queued": "call_queued",
            "call.in_progress": "call_started",
            "call.completed": "call_ended",
            "call.failed": "call_failed",
            "call.canceled": "call_canceled",
            "transcript.available": "transcript_available",
            "recording.available": "recording_available"
        }
        
        standardized_event = {
            "event_type": event_mapping.get(event_type, "unknown"),
            "provider_call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "provider_data": body
        }
        
        # Add event-specific data
        if event_type == "call.completed":
            standardized_event["duration"] = body.get("duration")
            standardized_event["call_status"] = "completed"
        elif event_type == "call.failed":
            standardized_event["error"] = body.get("error")
            standardized_event["call_status"] = "failed"
        elif event_type == "recording.available":
            standardized_event["recording_url"] = body.get("recordingUrl")
        
        # Add metadata if available
        if metadata := body.get("metadata"):
            standardized_event["lead_id"] = metadata.get("lead_id")
            standardized_event["campaign_id"] = metadata.get("campaign_id")
            standardized_event["gym_id"] = metadata.get("gym_id")
        
        return standardized_event 