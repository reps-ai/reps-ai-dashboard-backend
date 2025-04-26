"""
Implementation of the Campaign Management Service.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import uuid
import json

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
        """
        try:
            logger.info(f"Creating campaign with data: {campaign_data}")
            required_fields = ['name', 'branch_id']
            for field in required_fields:
                if field not in campaign_data:
                    raise ValueError(f"Missing required field: {field}")
            if 'campaign_status' not in campaign_data:
                campaign_data['campaign_status'] = 'not_started'

            # --- Fix: Ensure metrics is a plain dict and deeply serializable ---
            metrics = campaign_data.get("metrics")
            if metrics is None:
                campaign_data["metrics"] = {}
            elif hasattr(metrics, "dict"):
                campaign_data["metrics"] = metrics.dict()
            elif not isinstance(metrics, dict):
                try:
                    campaign_data["metrics"] = json.loads(metrics)
                except Exception:
                    campaign_data["metrics"] = {}
            # Deep copy to ensure no non-serializable types
            try:
                campaign_data["metrics"] = json.loads(json.dumps(campaign_data["metrics"]))
            except Exception as e:
                logger.error(f"Failed to serialize metrics: {e}")
                campaign_data["metrics"] = {}

            logger.info(f"Metrics before DB insert: {campaign_data['metrics']} (type: {type(campaign_data['metrics'])})")
            # --- End fix ---

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
            
            # Import here to avoid circular imports - use the new task_definitions module
            from ...tasks.campaign.task_definitions import schedule_campaign_task
            
            # Queue the task in Celery
            result = schedule_campaign_task.delay(campaign_id, target_date.isoformat())
            
            return [{"task_id": result.id, "status": "scheduled"}]
            
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
    
    async def list_campaigns(self, branch_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List campaigns for a branch with optional filtering.
        """
        try:
            logger.info(f"Listing campaigns for branch: {branch_id}")

            # Use repository method to apply all filters at the SQL level
            campaigns = await self.campaign_repository.filter_campaigns_by_branch(branch_id, filters)

            # No further filtering in Python; all filtering is done in SQL
            return campaigns

        except Exception as e:
            logger.error(f"Error listing campaigns for branch {branch_id}: {str(e)}")
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
    
    async def increment_call_count(self, campaign_id: str, count: int = 1) -> Dict[str, Any]:
        """
        Increment the call count for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            count: Number to increment by (default 1)
            
        Returns:
            Updated campaign data
        """
        logger.info(f"Incrementing call count for campaign {campaign_id} by {count}")
        try:
            result = await self.campaign_repository.increment_call_count(campaign_id, count)
            if not result:
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            return result
        except Exception as e:
            logger.error(f"Error incrementing call count: {str(e)}")
            raise ValueError(f"Failed to increment call count: {str(e)}")
    
    async def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Pause an active campaign to stop further call scheduling.
        
        Args:
            campaign_id: ID of the campaign to pause
            
        Returns:
            Dictionary containing the updated campaign details
            
        Raises:
            ValueError: If campaign not found or other error occurs
        """
        try:
            logger.info(f"Pausing campaign with ID: {campaign_id}")
            
            # Check if campaign exists
            existing_campaign = await self.campaign_repository.get_campaign_by_id(campaign_id)
            if not existing_campaign:
                logger.warning(f"Campaign with ID {campaign_id} not found")
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            
            # Only pause if campaign is active
            if existing_campaign.get('campaign_status') != 'active':
                logger.warning(f"Campaign with ID {campaign_id} is not active (status: {existing_campaign.get('campaign_status')})")
                return existing_campaign
            
            # Update campaign status to paused
            updated_campaign = await self.campaign_repository.update_campaign(campaign_id, {
                'campaign_status': 'paused'
            })
            
            logger.info(f"Successfully paused campaign with ID: {campaign_id}")
            return updated_campaign
            
        except ValueError as ve:
            # Re-raise the value errors with proper message
            raise ve
        except Exception as e:
            logger.error(f"Error pausing campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error pausing campaign: {str(e)}")
    
    async def cancel_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Cancel a campaign and revoke any scheduled tasks.
        
        Args:
            campaign_id: ID of the campaign to cancel
            
        Returns:
            Updated campaign data with cancelled status
        """
        try:
            logger.info(f"Cancelling campaign with ID: {campaign_id}")
            
            # Check if campaign exists
            campaign = await self.campaign_repository.get_campaign_by_id(campaign_id)
            if not campaign:
                logger.warning(f"Campaign with ID {campaign_id} not found")
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            
            # Update campaign status to cancelled
            updated_campaign = await self.campaign_repository.update_campaign(campaign_id, {
                'campaign_status': 'cancelled'
            })
            
            # Import celery app and revoke related tasks
            from ...celery_app import app
            
            # Query for tasks with this campaign_id
            i = app.control.inspect()
            scheduled_tasks = i.scheduled() or {}
            reserved_tasks = i.reserved() or {}
            active_tasks = i.active() or {}
            
            revoked_count = 0
            
            # Function to check if a task is for this campaign
            def is_campaign_task(task):
                # Check if it's a campaign-related task and if it contains our campaign_id
                return (
                    (task.get('name', '').startswith('campaign.') or
                     task.get('name', '').startswith('backend.tasks.campaign.'))
                    and
                    str(campaign_id) in str(task.get('args', []))
                )
            
            # Process scheduled tasks
            for worker, tasks in scheduled_tasks.items():
                for task in tasks:
                    if is_campaign_task(task):
                        task_id = task.get('id')
                        app.control.revoke(task_id, terminate=True)
                        logger.info(f"Revoked scheduled task: {task_id}")
                        revoked_count += 1
            
            # Process reserved tasks
            for worker, tasks in reserved_tasks.items():
                for task in tasks:
                    if is_campaign_task(task):
                        task_id = task.get('id')
                        app.control.revoke(task_id, terminate=True)
                        logger.info(f"Revoked reserved task: {task_id}")
                        revoked_count += 1
            
            # Process active tasks
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    if is_campaign_task(task):
                        task_id = task.get('id')
                        app.control.revoke(task_id, terminate=True)
                        logger.info(f"Revoked active task: {task_id}")
                        revoked_count += 1
            
            # Find and revoke any call tasks related to this campaign
            await self._revoke_call_tasks_for_campaign(campaign_id)
            
            logger.info(f"Successfully cancelled campaign {campaign_id}. Revoked {revoked_count} tasks.")
            return updated_campaign
            
        except ValueError as ve:
            # Re-raise the value errors with proper message
            raise ve
        except Exception as e:
            logger.error(f"Error cancelling campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error cancelling campaign: {str(e)}")
    
    async def _revoke_call_tasks_for_campaign(self, campaign_id: str) -> int:
        """
        Find and revoke call tasks for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Number of tasks revoked
        """
        from ...celery_app import app
        revoked_count = 0
        
        try:
            # Get all calls for this campaign
            calls = await self.campaign_repository.get_call_ids_for_campaign(campaign_id)
            
            # For each call, look for tasks with that call ID in args
            i = app.control.inspect()
            scheduled_tasks = i.scheduled() or {}
            
            # Function to check if a task is for a specific call
            def is_call_task(task, call_id):
                return (
                    task.get('name', '').startswith('call.')
                    and
                    str(call_id) in str(task.get('args', []))
                )
            
            # Revoke any scheduled call tasks
            for call_id in calls:
                for worker, tasks in scheduled_tasks.items():
                    for task in tasks:
                        if is_call_task(task, call_id):
                            task_id = task.get('id')
                            app.control.revoke(task_id, terminate=True)
                            logger.info(f"Revoked call task: {task_id} for call {call_id}")
                            revoked_count += 1
            
            return revoked_count
            
        except Exception as e:
            logger.error(f"Error revoking call tasks for campaign {campaign_id}: {str(e)}")
            return revoked_count
    
    async def get_campaign_leads(self, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Get all leads associated with a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            List of leads for the campaign
            
        Raises:
            ValueError: If campaign not found or other error occurs
        """
        try:
            logger.info(f"Getting leads for campaign: {campaign_id}")
            
            # Check if campaign exists
            campaign = await self.campaign_repository.get_campaign_by_id(campaign_id)
            if not campaign:
                logger.warning(f"Campaign with ID {campaign_id} not found")
                raise ValueError(f"Campaign with ID {campaign_id} not found")
            
            # Get campaign leads
            leads = await self.campaign_repository.get_campaign_leads(campaign_id)
            
            # Each lead needs to have a lead_id field for compatibility with older code
            for lead in leads:
                if 'id' in lead and 'lead_id' not in lead:
                    lead['lead_id'] = lead['id']
            
            return leads
            
        except ValueError as ve:
            raise ve
        except Exception as e:
            logger.error(f"Error retrieving leads for campaign {campaign_id}: {str(e)}")
            raise ValueError(f"Error retrieving campaign leads: {str(e)}")
