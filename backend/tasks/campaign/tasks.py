"""
Campaign scheduling task implementations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_
from contextlib import asynccontextmanager

from ...db.connections.database import get_db
from ...db.models.campaign.follow_up_campaign import FollowUpCampaign
from ...utils.logging.logger import get_logger

# Import helper modules
from .lead_prioritization import prioritize_leads, get_lead_last_call_outcome
from .call_scheduling import create_scheduled_calls
from .campaign_helpers import db_session

# Configure logging
logger = get_logger(__name__)

# Constants
CALL_HOURS_START = datetime.strptime("18:00", "%H:%M").time()  # 6 PM
CALL_HOURS_END = datetime.strptime("21:00", "%H:%M").time()    # 9 PM


class CampaignSchedulingService:
    """
    Service for scheduling campaign calls.
    """
    
    async def schedule_calls_for_campaign(
        self, 
        campaign_id: str, 
        target_date: Optional[date] = None,
        get_session=None
    ) -> List[Dict[str, Any]]:
        """
        Schedule calls for a campaign on a specific date.
        
        Args:
            campaign_id: ID of the campaign
            target_date: Date to schedule calls for (defaults to today)
            get_session: Function to provide a database session
            
        Returns:
            List of scheduled calls
        """
        if target_date is None:
            target_date = date.today()
            
        logger.info(f"Scheduling calls for campaign {campaign_id} on {target_date}")
        
        # Use the provided session factory or fall back to our custom db_session context manager
        if get_session is None:
            get_session = db_session
        
        async with get_session() as session:
            # Create service instances with proper repositories
            from ...services.campaign.factory import create_campaign_service_async
            from ...services.call.factory import create_call_service_async
            
            campaign_service = await create_campaign_service_async()
            call_service = await create_call_service_async()
            
            # 1. Get the campaign details
            campaign = await campaign_service.get_campaign(campaign_id)
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found")
                return []
            
            # Debug output the actual campaign data to understand why frequency is 0
            logger.info(f"Campaign details: frequency={campaign.get('frequency')}, type={type(campaign.get('frequency'))}")
            logger.info(f"Campaign data type: {type(campaign)}")
            
            # Let's log the whole campaign object to see all its data
            logger.info(f"Full campaign data: {campaign}")
            
            # Check if campaign is active based on date range and status
            campaign_start_date = campaign.get('start_date')
            campaign_end_date = campaign.get('end_date')
            campaign_status = campaign.get('campaign_status')
            current_date = datetime.now().date()
            
            # Convert datetime objects to date for comparison
            if campaign_start_date and isinstance(campaign_start_date, datetime):
                campaign_start_date = campaign_start_date.date()
            if campaign_end_date and isinstance(campaign_end_date, datetime):
                campaign_end_date = campaign_end_date.date()
            
            # Check campaign status - only not_started or paused campaigns should be scheduled
            # active means it's already running, cancelled means it's terminated, completed means it's done
            if campaign_status not in ['not_started', 'paused']:
                logger.info(f"Campaign {campaign_id} has status '{campaign_status}', cannot be scheduled. Valid statuses for scheduling are 'not_started' or 'paused'")
                return []
                
            is_active = True
            if campaign_start_date and current_date < campaign_start_date:
                is_active = False
            if campaign_end_date and current_date > campaign_end_date:
                is_active = False
                
            # Skip if campaign is not active based on date range
            if not is_active:
                logger.info(f"Campaign {campaign_id} is not active (outside date range), skipping scheduling")
                return []
            
            # 2. Check if the target date is within the campaign date range
            # Get schedule from metrics JSON field, not directly from campaign
            metrics = campaign.get('metrics', {}) or {}
            schedule = metrics.get('schedule', {}) or {}
            
            # Use campaign start/end dates as defaults if schedule doesn't specify them
            schedule_start_date = None
            schedule_end_date = None
            
            # Only try to access these if schedule contains them
            if 'start_date' in schedule:
                schedule_start_date = schedule.get('start_date')
                if isinstance(schedule_start_date, str):
                    try:
                        schedule_start_date = datetime.fromisoformat(schedule_start_date).date()
                    except ValueError:
                        schedule_start_date = None
                elif isinstance(schedule_start_date, datetime):
                    schedule_start_date = schedule_start_date.date()
            
            if 'end_date' in schedule:
                schedule_end_date = schedule.get('end_date')
                if isinstance(schedule_end_date, str):
                    try:
                        schedule_end_date = datetime.fromisoformat(schedule_end_date).date()
                    except ValueError:
                        schedule_end_date = None
                elif isinstance(schedule_end_date, datetime):
                    schedule_end_date = schedule_end_date.date()
            
            # Use schedule dates if available, otherwise fall back to campaign dates
            start_date = schedule_start_date or campaign_start_date
            end_date = schedule_end_date or campaign_end_date
            
            if start_date and target_date < start_date:
                logger.info(f"Target date {target_date} is before campaign start date {start_date}, skipping")
                return []
                
            if end_date and target_date > end_date:
                logger.info(f"Target date {target_date} is after campaign end date {end_date}, skipping")
                return []
            
            # 3. Check if the target day is a valid call day for the campaign
            weekday = target_date.strftime('%a').lower()
            call_days = schedule.get('call_days', [])
            
            if call_days and weekday not in call_days:
                logger.info(f"Target day {weekday} is not in allowed call days: {call_days}, skipping")
                return []
            
            # 4. Get the number of calls to schedule based on frequency
            # Check both 'frequency' and 'period' fields due to to_dict() mapping in model
            frequency = campaign.get('frequency', 0)
            if frequency == 0:
                # Try period as a fallback
                frequency = campaign.get('period', 0)
                
            # Force to integer for postgres JSON response compatibility
            try:
                frequency = int(frequency)
            except (TypeError, ValueError):
                # Default to 5 if frequency can't be parsed
                logger.warning(f"Invalid frequency value for campaign {campaign_id}, defaulting to 5")
                frequency = 5
                
            logger.info(f"Using frequency value: {frequency} for campaign {campaign_id}")
            
            if frequency <= 0:
                # If we still have 0 frequency, update it to a valid value
                logger.warning(f"Campaign {campaign_id} has zero frequency, updating to 5")
                await campaign_service.update_campaign(campaign_id, {'frequency': 5})
                frequency = 5
            
            if frequency <= 0:
                logger.info(f"Campaign {campaign_id} has frequency set to {frequency}, skipping")
                return []
            
            # Check if we've already reached the maximum number of calls for this campaign
            # Use call_count field directly from the campaign data
            call_count = campaign.get('call_count', 0)
            
            if call_count >= frequency:
                logger.info(f"Campaign {campaign_id} has already reached its maximum number of calls ({frequency}), marking as completed")
                await campaign_service.update_campaign(campaign_id, {'end_date': current_date})
                return []
            
            # Calculate how many calls to schedule today
            remaining_calls = frequency - call_count
            max_daily_calls = schedule.get('max_daily_calls', 10)  # Default to 10 calls per day
            calls_to_schedule = min(remaining_calls, max_daily_calls)
            
            # 5. Get prioritized leads for the campaign
            scheduled_calls = await self._schedule_campaign_leads(
                campaign_service, 
                call_service, 
                campaign, 
                campaign_id, 
                session, 
                target_date, 
                calls_to_schedule
            )
            
            # After scheduling calls, update call count and metrics
            new_call_count = call_count + len(scheduled_calls)
            
            # Update campaign metrics with comprehensive details
            metrics = campaign.get('metrics', {}) or {}
            
            # Initialize metrics if needed
            if 'scheduled_calls' not in metrics:
                metrics['scheduled_calls'] = 0
            if 'outcomes' not in metrics:
                metrics['outcomes'] = {}
            if 'errors' not in metrics:
                metrics['errors'] = 0
            if 'failed_calls' not in metrics:
                metrics['failed_calls'] = 0
            
            # Update metrics
            metrics['scheduled_calls'] += len(scheduled_calls)
            metrics['last_scheduled_date'] = target_date.isoformat()
            
            await campaign_service.update_campaign(campaign_id, {
                'metrics': metrics,
                'call_count': new_call_count  # Use the dedicated call_count column
            })
            
            # After successfully scheduling calls, update status to active if it was not_started
            if campaign_status == 'not_started' and len(scheduled_calls) > 0:
                await campaign_service.update_campaign(campaign_id, {
                    'campaign_status': 'active'
                })
                logger.info(f"Updated campaign {campaign_id} status from not_started to active")
            
            # If we've scheduled all the required calls, mark the campaign as complete
            if new_call_count >= frequency:
                logger.info(f"Campaign {campaign_id} has reached its target frequency, marking as inactive")
                await campaign_service.update_campaign(campaign_id, {'end_date': current_date})
            
            logger.info(f"Scheduled {len(scheduled_calls)} calls for campaign {campaign_id}")
            return scheduled_calls

    async def _schedule_campaign_leads(
        self,
        campaign_service,
        call_service,
        campaign,
        campaign_id,
        session,
        target_date,
        calls_to_schedule
    ) -> List[Dict[str, Any]]:
        """
        Helper method to schedule leads for a campaign.
        """
        # First get all leads associated with the campaign
        campaign_leads = await campaign_service.get_campaign_leads(campaign_id)
        
        lead_ids = [lead.get('lead_id') for lead in campaign_leads]
        if not lead_ids:
            logger.info(f"No leads found for campaign {campaign_id}, skipping")
            return []
        
        # Get detailed lead data for prioritization
        from ...services.lead.factory import LeadServiceFactory
        lead_service = await LeadServiceFactory.create_service(session)
        
        leads = []
        for lead_id in lead_ids:
            try:
                lead = await lead_service.get_lead(lead_id)
                if lead:
                    leads.append(lead)
            except Exception as e:
                logger.error(f"Error retrieving lead {lead_id}: {str(e)}")
        
        # Get both completed calls from call logs AND scheduled calls from the scheduled_calls table
        today_start = datetime.combine(target_date, datetime.min.time())
        today_end = datetime.combine(target_date, datetime.max.time())
        
        # 1. Get completed calls from call logs
        completed_calls = await call_service.get_calls_by_date_range(
            campaign.get('branch_id'),
            today_start,
            today_end
        )
        
        # 2. Get pending scheduled calls that haven't been processed yet
        try:
            scheduled_calls = await call_service.get_scheduled_calls_by_date_range(
                campaign.get('branch_id'),
                today_start,
                today_end
            )
            scheduled_calls = scheduled_calls.get("calls", [])
        except (AttributeError, Exception) as e:
            logger.error(f"Error getting scheduled calls: {str(e)}")
            scheduled_calls = []
        
        # Combine both lists of lead IDs to exclude
        exclude_lead_ids = [call.get('lead_id') for call in completed_calls]
        exclude_lead_ids.extend([call.get('lead_id') for call in scheduled_calls])
        
        # Remove duplicates
        exclude_lead_ids = list(set(exclude_lead_ids))
        
        # Filter out leads that already have calls today (completed or scheduled)
        leads = [lead for lead in leads if lead.get('id') not in exclude_lead_ids]
        
        # Get last call outcomes for all leads from call logs
        call_outcomes = {}
        for lead in leads:
            lead_id = str(lead.get('id'))
            outcome = await get_lead_last_call_outcome(call_service, lead_id)
            if outcome:
                call_outcomes[lead_id] = outcome
        
        # Get prioritized leads based on various criteria - use lead_status not status
        # Exclude leads with outcome "not_interested" and lead_status "converted"
        prioritized_leads = prioritize_leads(leads, campaign.get('gap', 7), call_outcomes)
        prioritized_leads = prioritized_leads[:calls_to_schedule]
        
        # Schedule calls for the prioritized leads
        return await create_scheduled_calls(
            prioritized_leads, campaign_id, target_date, CALL_HOURS_START, CALL_HOURS_END
        )

    async def schedule_calls_for_all_campaigns(self, target_date: Optional[date] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Schedule calls for all active campaigns on a specific date.
        
        Args:
            target_date: Date to schedule calls for (defaults to today)
            
        Returns:
            Dictionary mapping campaign IDs to lists of scheduled calls
        """
        if target_date is None:
            target_date = date.today()
            
        logger.info(f"Scheduling calls for all active campaigns on {target_date}")
        
        # Use our new db_session context manager instead of get_db directly
        async with db_session() as session:
            # Use the async campaign service
            from ...services.campaign.factory import create_campaign_service_async
            campaign_service = await create_campaign_service_async()
            
            try:
                current_date = datetime.now().date()
                
                # Query all active campaigns
                query = select(FollowUpCampaign).where(
                    and_(
                        or_(
                            FollowUpCampaign.start_date == None,
                            FollowUpCampaign.start_date <= current_date
                        ),
                        or_(
                            FollowUpCampaign.end_date == None,
                            FollowUpCampaign.end_date >= current_date
                        )
                    )
                )
                
                result = await session.execute(query)
                active_campaigns = result.scalars().all()
                
                if not active_campaigns:
                    logger.info("No active campaigns found")
                    return {}
                    
                logger.info(f"Found {len(active_campaigns)} active campaigns")
                
                results = {}
                for campaign in active_campaigns:
                    try:
                        campaign_id = str(campaign.id)
                        scheduled_calls = await self.schedule_calls_for_campaign(campaign_id, target_date)
                        results[campaign_id] = scheduled_calls
                    except Exception as e:
                        logger.error(f"Error scheduling calls for campaign {campaign.id}: {str(e)}")
                
                return results
            except Exception as e:
                logger.error(f"Error retrieving active campaigns: {str(e)}")
                return {}
