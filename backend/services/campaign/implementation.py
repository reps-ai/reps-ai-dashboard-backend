"""
Implementation of the Campaign Management Service.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid

from .interface import CampaignService
from ...db.repositories.campaign import CampaignRepository
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

class DefaultCampaignService(CampaignService):
    """
    Default implementation of the Campaign Management Service.
    """
    
    def __init__(self, campaign_repository: CampaignRepository):
        """
        Initialize the campaign service.
        
        Args:
            campaign_repository: Repository for campaign operations
        """
        self.campaign_repository = campaign_repository
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new call campaign.
        
        Args:
            campaign_data: Dictionary containing campaign configuration
            
        Returns:
            Dictionary containing the created campaign details
            
        Raises:
            ValueError: If there's an error creating the campaign
        """
        try:
            logger.info(f"Creating campaign with data: {campaign_data}")
            
            # Validate required fields
            required_fields = ['name', 'gym_id']
            for field in required_fields:
                if field not in campaign_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Format schedule data if present
            if schedule_data := campaign_data.get('schedule'):
                # Ensure dates are in the correct format
                if 'start_date' in schedule_data and isinstance(schedule_data['start_date'], str):
                    schedule_data['start_date'] = datetime.fromisoformat(schedule_data['start_date'].replace('Z', '+00:00'))
                
                if 'end_date' in schedule_data and isinstance(schedule_data['end_date'], str):
                    schedule_data['end_date'] = datetime.fromisoformat(schedule_data['end_date'].replace('Z', '+00:00'))
            
            # Create campaign using repository
            campaign = await self.campaign_repository.create_campaign(campaign_data)
            
            logger.info(f"Created campaign with ID: {campaign.get('id')}")
            return campaign
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            raise ValueError(f"Failed to create campaign: {str(e)}")
    
    async def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign details by ID.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dictionary containing campaign details
            
        Raises:
            ValueError: If campaign not found or other error occurs
        """
        try:
            logger.info(f"Getting campaign with ID: {campaign_id}")
            
            campaign = await self.campaign_repository.get_campaign_by_id(campaign_id)
            
            if not campaign:
                logger.warning(f"Campaign with ID {campaign_id} not found")
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            
            # Get schedule information
            schedule = await self.campaign_repository.get_campaign_schedule(campaign_id)
            if schedule:
                campaign['schedule'] = schedule
            
            return campaign
            
        except ValueError as ve:
            # Re-raise the value errors with proper message
            raise ve
        except Exception as e:
            logger.error(f"Error retrieving campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error retrieving campaign: {str(e)}")
    
    async def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing campaign.
        
        Args:
            campaign_id: ID of the campaign to update
            campaign_data: Dictionary containing updated campaign configuration
            
        Returns:
            Dictionary containing the updated campaign details
            
        Raises:
            ValueError: If campaign not found or other error occurs
        """
        try:
            logger.info(f"Updating campaign with ID: {campaign_id} with data: {campaign_data}")
            
            # Check if campaign exists
            existing_campaign = await self.campaign_repository.get_campaign_by_id(campaign_id)
            if not existing_campaign:
                logger.warning(f"Campaign with ID {campaign_id} not found")
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            
            # Extract schedule data if present
            schedule_data = campaign_data.pop('schedule', None)
            
            # Update campaign basic information
            if campaign_data:
                updated_campaign = await self.campaign_repository.update_campaign(campaign_id, campaign_data)
                if not updated_campaign:
                    raise ValueError(f"Failed to update campaign {campaign_id}")
            else:
                updated_campaign = existing_campaign
            
            # Update schedule if provided
            if schedule_data:
                updated_schedule = await self.campaign_repository.update_campaign_schedule(campaign_id, schedule_data)
                updated_campaign['schedule'] = updated_schedule
            
            logger.info(f"Updated campaign with ID: {campaign_id}")
            return updated_campaign
            
        except ValueError as ve:
            # Re-raise the value errors with proper message
            raise ve
        except Exception as e:
            logger.error(f"Error updating campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error updating campaign: {str(e)}")
    
    async def delete_campaign(self, campaign_id: str) -> bool:
        """
        Delete a campaign.
        
        Args:
            campaign_id: ID of the campaign to delete
            
        Returns:
            True if deletion was successful, False otherwise
            
        Raises:
            ValueError: If campaign not found or other error occurs
        """
        try:
            logger.info(f"Deleting campaign with ID: {campaign_id}")
            
            # Check if campaign exists
            existing_campaign = await self.campaign_repository.get_campaign_by_id(campaign_id)
            if not existing_campaign:
                logger.warning(f"Campaign with ID {campaign_id} not found")
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            
            # Delete the campaign
            result = await self.campaign_repository.delete_campaign(campaign_id)
            
            if not result:
                logger.warning(f"Failed to delete campaign with ID {campaign_id}")
                raise ValueError(f"Failed to delete campaign with ID {campaign_id}")
            
            logger.info(f"Successfully deleted campaign with ID: {campaign_id}")
            return True
            
        except ValueError as ve:
            # Re-raise the value errors with proper message
            raise ve
        except Exception as e:
            logger.error(f"Error deleting campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error deleting campaign: {str(e)}")
    
    async def schedule_calls(self, campaign_id: str, target_date: datetime) -> List[Dict[str, Any]]:
        """
        Schedule calls for a specific date based on campaign configuration.
        
        Args:
            campaign_id: ID of the campaign
            target_date: Date to schedule calls for
            
        Returns:
            List of scheduled calls
            
        Raises:
            ValueError: If campaign not found or other error occurs
        """
        try:
            logger.info(f"Scheduling calls for campaign {campaign_id} on {target_date}")
            
            # Check if campaign exists and is active
            campaign = await self.campaign_repository.get_campaign_by_id(campaign_id)
            if not campaign:
                logger.warning(f"Campaign with ID {campaign_id} not found")
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            
            if not campaign.get('is_active', False):
                logger.warning(f"Campaign with ID {campaign_id} is not active")
                raise ValueError(f"Campaign with ID {campaign_id} is not active")
            
            # Get campaign schedule
            schedule = await self.campaign_repository.get_campaign_schedule(campaign_id)
            if not schedule:
                logger.warning(f"No schedule found for campaign {campaign_id}")
                raise ValueError(f"No schedule found for campaign {campaign_id}")
            
            # Check if the target date is within the campaign date range
            start_date = schedule.get('start_date')
            end_date = schedule.get('end_date')
            
            if start_date and target_date.date() < start_date:
                logger.warning(f"Target date {target_date.date()} is before campaign start date {start_date}")
                raise ValueError(f"Target date is before campaign start date")
            
            if end_date and target_date.date() > end_date:
                logger.warning(f"Target date {target_date.date()} is after campaign end date {end_date}")
                raise ValueError(f"Target date is after campaign end date")
            
            # Check if the target day is allowed by campaign settings
            weekday = target_date.strftime('%a').lower()
            call_days = schedule.get('call_days', [])
            
            if call_days and weekday not in call_days:
                logger.warning(f"Target day {weekday} is not in allowed call days: {call_days}")
                raise ValueError(f"Target day is not in allowed call days")
            
            # Get leads associated with the campaign
            campaign_leads = await self.campaign_repository.get_campaign_leads(campaign_id)
            
            # In a real implementation, you would create call records for each lead
            # based on campaign settings, call history, etc.
            # This is a simplified placeholder implementation
            scheduled_calls = []
            
            # Note: The actual scheduling logic would typically be more complex
            # and would be implemented in a background task or Celery worker
            logger.info(f"Scheduled {len(scheduled_calls)} calls for campaign {campaign_id}")
            return scheduled_calls
            
        except ValueError as ve:
            # Re-raise the value errors with proper message
            raise ve
        except Exception as e:
            logger.error(f"Error scheduling calls for campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error scheduling calls for campaign: {str(e)}")
    
    async def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get metrics for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dictionary containing campaign metrics
            
        Raises:
            ValueError: If campaign not found or other error occurs
        """
        try:
            logger.info(f"Getting metrics for campaign: {campaign_id}")
            
            # Check if campaign exists
            campaign = await self.campaign_repository.get_campaign_by_id(campaign_id)
            if not campaign:
                logger.warning(f"Campaign with ID {campaign_id} not found")
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            
            # Get existing metrics if any
            existing_metrics = campaign.get('metrics', {})
            
            # In a real implementation, you would calculate current metrics
            # based on call logs, lead status, etc.
            # This is a simplified placeholder implementation
            
            return existing_metrics
            
        except ValueError as ve:
            # Re-raise the value errors with proper message
            raise ve
        except Exception as e:
            logger.error(f"Error retrieving metrics for campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error retrieving campaign metrics: {str(e)}")
    
    async def list_campaigns(self, gym_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List campaigns for a gym with optional filtering.
        
        Args:
            gym_id: ID of the gym
            filters: Optional filters for the campaigns
            
        Returns:
            List of campaigns matching the criteria
            
        Raises:
            ValueError: If an error occurs during retrieval
        """
        try:
            logger.info(f"Listing campaigns for gym: {gym_id}")
            
            # Get active campaigns for the gym
            campaigns = await self.campaign_repository.get_active_campaigns(gym_id)
            
            # Apply filters if provided
            if filters:
                filtered_campaigns = []
                
                # Filter by date if specified
                if 'date' in filters:
                    target_date = filters['date']
                    if isinstance(target_date, str):
                        target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00')).date()
                    elif isinstance(target_date, datetime):
                        target_date = target_date.date()
                    
                    # Get campaigns scheduled for the target date
                    date_campaigns = await self.campaign_repository.get_campaigns_for_date(target_date)
                    campaign_ids = {campaign['id'] for campaign in date_campaigns}
                    
                    # Keep only campaigns that match both gym_id and date criteria
                    filtered_campaigns = [campaign for campaign in campaigns if campaign['id'] in campaign_ids]
                else:
                    filtered_campaigns = campaigns
                
                # Apply other filters as needed
                # ...
                
                return filtered_campaigns
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Error listing campaigns for gym {gym_id}: {str(e)}")
            raise ValueError(f"Error listing campaigns: {str(e)}")
            
    # Additional helper methods for campaign management
    
    async def add_leads_to_campaign(self, campaign_id: str, lead_ids: List[str]) -> bool:
        """
        Add leads to a campaign.
        
        Args:
            campaign_id: ID of the campaign
            lead_ids: List of lead IDs to add
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If campaign not found or other error occurs
        """
        try:
            logger.info(f"Adding {len(lead_ids)} leads to campaign: {campaign_id}")
            
            # Check if campaign exists
            campaign = await self.campaign_repository.get_campaign_by_id(campaign_id)
            if not campaign:
                logger.warning(f"Campaign with ID {campaign_id} not found")
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            
            # Add leads to campaign
            result = await self.campaign_repository.add_leads_to_campaign(campaign_id, lead_ids)
            
            if result:
                logger.info(f"Successfully added {len(lead_ids)} leads to campaign {campaign_id}")
            else:
                logger.warning(f"Failed to add leads to campaign {campaign_id}")
            
            return result
            
        except ValueError as ve:
            # Re-raise the value errors with proper message
            raise ve
        except Exception as e:
            logger.error(f"Error adding leads to campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error adding leads to campaign: {str(e)}")
    
    async def remove_leads_from_campaign(self, campaign_id: str, lead_ids: List[str]) -> bool:
        """
        Remove leads from a campaign.
        
        Args:
            campaign_id: ID of the campaign
            lead_ids: List of lead IDs to remove
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If campaign not found or other error occurs
        """
        try:
            logger.info(f"Removing {len(lead_ids)} leads from campaign: {campaign_id}")
            
            # Check if campaign exists
            campaign = await self.campaign_repository.get_campaign_by_id(campaign_id)
            if not campaign:
                logger.warning(f"Campaign with ID {campaign_id} not found")
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            
            # Remove leads from campaign
            result = await self.campaign_repository.remove_leads_from_campaign(campaign_id, lead_ids)
            
            if result:
                logger.info(f"Successfully removed leads from campaign {campaign_id}")
            else:
                logger.warning(f"Failed to remove leads from campaign {campaign_id} or no leads were found")
            
            return result
            
        except ValueError as ve:
            # Re-raise the value errors with proper message
            raise ve
        except Exception as e:
            logger.error(f"Error removing leads from campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error removing leads from campaign: {str(e)}")
