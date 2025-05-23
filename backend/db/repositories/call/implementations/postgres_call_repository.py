"""
PostgreSQL implementation of the CallRepository interface.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select, and_, or_, func, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ...call.interface import CallRepository
from ....models.call.call_log import CallLog
from ....models.lead import Lead
from ....models.campaign.follow_up_campaign import FollowUpCampaign
from ....models.call.follow_up_call import FollowUpCall
from ....models.user import User
from ....models.gym.branch import Branch
import uuid
from ....helpers.call.call_queries import (
    get_call_with_related_data,
    get_calls_by_campaign_db,
    get_calls_by_lead_db,
    get_calls_by_date_range_db,
    get_calls_by_outcome_db,
    update_call_metrics_db,
    get_filtered_calls_db,
    update_call_recording_db,  # Add this
    update_call_transcript_db,  # Add this
    get_scheduled_calls_db     # Add this
)
from .....utils.logging.logger import get_logger

logger = get_logger(__name__)

class PostgresCallRepository(CallRepository):
    """PostgreSQL implementation of the CallRepository interface."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with a database session."""
        self.session = session
    
    #Works
    async def create_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new call record.
        
        Args:
            call_data: Dictionary containing call details
            
        Returns:
            Dictionary containing the created call data
        """
        logger.info(f"Creating new call record")
        
        # Create new call log
        new_call = CallLog(**call_data)
        self.session.add(new_call)
        await self.session.commit()
        await self.session.refresh(new_call)
        
        return new_call.to_dict()
    
    #Works
    async def get_call_by_id(self, call_id: str) -> Optional[Dict[str, Any]]:
        """
        Get call details by ID.
        
        Args:
            call_id: Unique identifier of the call
            
        Returns:
            Call data if found, None otherwise
        """
        logger.info(f"Getting call with ID: {call_id}")
        try:
            return await get_call_with_related_data(self.session, call_id)
        except Exception as e:
            logger.error(f"Error getting call by ID {call_id}: {str(e)}")
            raise
    
    #Works
    async def update_call(self, call_id: str, call_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update call details.
        
        Args:
            call_id: Unique identifier of the call
            call_data: Dictionary containing updated call details
            
        Returns:
            Updated call data if successful, None if call not found
        """
        logger.info(f"Updating call with ID: {call_id}")
        
        # Check if call exists
        call_query = select(CallLog).where(CallLog.id == call_id)
        call_result = await self.session.execute(call_query)
        call = call_result.scalar_one_or_none()
        
        if not call:
            logger.warning(f"Call with ID {call_id} not found")
            return None
        
        # Update call
        update_query = update(CallLog).where(CallLog.id == call_id).values(**call_data)
        await self.session.execute(update_query)
        await self.session.commit()
        
        # Get updated call data
        return await get_call_with_related_data(self.session, call_id)
    
    #Works
    async def delete_call(self, call_id: str) -> bool:
        """
        Delete a call record.
        
        Args:
            call_id: Unique identifier of the call
            
        Returns:
            True if successful, False if call not found
        """
        logger.info(f"Deleting call with ID: {call_id}")
        
        # Check if call exists
        call_query = select(CallLog).where(CallLog.id == call_id)
        call_result = await self.session.execute(call_query)
        call = call_result.scalar_one_or_none()
        
        if not call:
            logger.warning(f"Call with ID {call_id} not found")
            return False
        
        # Delete call
        delete_query = delete(CallLog).where(CallLog.id == call_id)
        await self.session.execute(delete_query)
        await self.session.commit()
        
        return True
    
    ##Errors
    async def get_calls_by_campaign(
        self, 
        campaign_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get calls for a campaign with pagination.
        
        Args:
            campaign_id: Campaign ID
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info
        """
        logger.info(f"Getting calls for campaign: {campaign_id}")
        return await get_calls_by_campaign_db(self.session, campaign_id, page, page_size)
    
    #Works
    async def get_calls_by_lead(
        self, 
        lead_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get calls for a lead with pagination.
        
        Args:
            lead_id: Lead ID
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info
        """
        logger.info(f"Getting calls for lead: {lead_id}")
        return await get_calls_by_lead_db(self.session, lead_id, page, page_size)

    #Works
    async def get_calls_by_date_range(
        self, 
        branch_id: str, 
        start_date: datetime, 
        end_date: datetime,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get calls within a date range with pagination.
        
        Args:
            branch_id: Branch ID
            start_date: Start of the date range
            end_date: End of the date range
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info
        """
        logger.info(f"Getting calls for branch {branch_id} from {start_date} to {end_date}")
        
        # Ensure branch_id is a UUID
        branch_uuid = branch_id if isinstance(branch_id, uuid.UUID) else uuid.UUID(str(branch_id))
        
        return await get_calls_by_date_range_db(
            self.session, branch_uuid, start_date, end_date, page, page_size
        )
    

    #Optional
    async def get_scheduled_calls(
        self, 
        branch_id: str,  # Changed from gym_id to branch_id 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get scheduled calls for a time period.
        
        Args:
            branch_id: Branch ID to filter by 
            start_time: Start of the time period
            end_time: End of the time period
            
        Returns:
            List of scheduled call data
        """
        logger.info(f"Getting scheduled calls for branch {branch_id} from {start_time} to {end_time}")
        return await get_scheduled_calls_db(self.session, branch_id, start_time, end_time)
    
    async def get_calls_by_outcome(
        self, 
        branch_id: str, 
        outcome: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get calls by outcome with pagination.
        
        Args:
            branch_id: Branch ID
            outcome: Outcome to filter by
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing calls and pagination info
        """
        logger.info(f"Getting calls for branch {branch_id} with outcome: {outcome}")
        return await get_calls_by_outcome_db(self.session, branch_id, outcome, page, page_size)
    
    #Optional
    async def update_call_recording(
        self, 
        call_id: str, 
        recording_url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update call recording URL.
        
        Args:
            call_id: Call ID
            recording_url: URL of the recording
            
        Returns:
            Updated call data if successful, None if call not found
        """
        logger.info(f"Updating recording for call: {call_id}")
        return await update_call_recording_db(self.session, call_id, recording_url)
    
    #Optional
    async def update_call_transcript(
        self, 
        call_id: str, 
        transcript: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update call transcript.
        
        Args:
            call_id: Call ID
            transcript: Call transcript text
            
        Returns:
            Updated call data if successful, None if call not found
        """
        logger.info(f"Updating transcript for call: {call_id}")
        return await update_call_transcript_db(self.session, call_id, transcript)
    
    #Optional
    async def update_call_metrics(
        self, 
        call_id: str, 
        metrics_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update call metrics.
        
        Args:
            call_id: Call ID
            metrics_data: Dictionary containing metric updates
            
        Returns:
            Updated call data if successful, None if call not found
        """
        logger.info(f"Updating metrics for call: {call_id}")
        return await update_call_metrics_db(self.session, call_id, metrics_data)

    async def get_calls_with_filters(
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
        Get calls with combined filtering at the database level.
        
        Args:
            branch_id: ID of the branch (required for security)
            page: Page number
            page_size: Page size
            lead_id: Optional lead ID to filter by
            campaign_id: Optional campaign ID to filter by
            direction: Optional call direction to filter by (inbound/outbound)
            outcome: Optional outcome to filter by
            start_date: Optional start date for date range filtering
            end_date: Optional end date for date range filtering
            
        Returns:
            Dictionary containing calls and pagination info
        """
        
        # Ensure branch_id is a UUID
        branch_uuid = branch_id if isinstance(branch_id, uuid.UUID) else uuid.UUID(str(branch_id))
        
        logger.info(f"Getting filtered calls with combined criteria: branch_id={branch_uuid}, "
                    f"lead_id={lead_id}, campaign_id={campaign_id}, direction={direction}, "
                    f"outcome={outcome}")
        
        return await get_filtered_calls_db(
            self.session,
            branch_uuid,  # Now guaranteed to be a UUID
            page,
            page_size,
            lead_id=lead_id,
            campaign_id=campaign_id,
            direction=direction,
            outcome=outcome,
            start_date=start_date,
            end_date=end_date
        )

    """Optional From this point"""

    """"""
    async def create_follow_up_call(
        self, 
        follow_up_call_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new follow-up call record.
        
        Args:
            follow_up_call_data: Dictionary containing follow-up call details
            
        Returns:
            Dictionary containing the created follow-up call data
        """
        logger.info(f"Creating new follow-up call record")
        
        # Create new follow-up call
        new_follow_up_call = FollowUpCall(**follow_up_call_data)
        self.session.add(new_follow_up_call)
        await self.session.commit()
        await self.session.refresh(new_follow_up_call)
        
        return new_follow_up_call.to_dict()
    
    async def get_follow_up_call_by_id(
        self, 
        follow_up_call_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get follow-up call details by ID.
        
        Args:
            follow_up_call_id: Unique identifier of the follow-up call
            
        Returns:
            Follow-up call data if found, None otherwise
        """
        logger.info(f"Getting follow-up call with ID: {follow_up_call_id}")
        
        # Get follow-up call
        follow_up_call_query = select(FollowUpCall).where(FollowUpCall.id == follow_up_call_id)
        follow_up_call_result = await self.session.execute(follow_up_call_query)
        follow_up_call = follow_up_call_result.scalar_one_or_none()
        
        if not follow_up_call:
            return None
        
        return follow_up_call.to_dict()
    
    async def update_follow_up_call(
        self, 
        follow_up_call_id: str, 
        follow_up_call_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update follow-up call details.
        
        Args:
            follow_up_call_id: Unique identifier of the follow-up call
            follow_up_call_data: Dictionary containing updated follow-up call details
            
        Returns:
            Updated follow-up call data if successful, None if follow-up call not found
        """
        logger.info(f"Updating follow-up call with ID: {follow_up_call_id}")
        
        # Check if follow-up call exists
        follow_up_call_query = select(FollowUpCall).where(FollowUpCall.id == follow_up_call_id)
        follow_up_call_result = await self.session.execute(follow_up_call_query)
        follow_up_call = follow_up_call_result.scalar_one_or_none()
        
        if not follow_up_call:
            logger.warning(f"Follow-up call with ID {follow_up_call_id} not found")
            return None
        
        # Update follow-up call
        update_query = update(FollowUpCall).where(FollowUpCall.id == follow_up_call_id).values(**follow_up_call_data)
        await self.session.execute(update_query)
        await self.session.commit()
        
        # Get updated follow-up call data
        follow_up_call_query = select(FollowUpCall).where(FollowUpCall.id == follow_up_call_id)
        follow_up_call_result = await self.session.execute(follow_up_call_query)
        updated_follow_up_call = follow_up_call_result.scalar_one_or_none()
        
        return updated_follow_up_call.to_dict()
    
    async def delete_follow_up_call(self, follow_up_call_id: str) -> bool:
        """
        Delete a follow-up call record.
        
        Args:
            follow_up_call_id: Unique identifier of the follow-up call
            
        Returns:
            True if successful, False if follow-up call not found
        """
        logger.info(f"Deleting follow-up call with ID: {follow_up_call_id}")
        
        # Check if follow-up call exists
        follow_up_call_query = select(FollowUpCall).where(FollowUpCall.id == follow_up_call_id)
        follow_up_call_result = await self.session.execute(follow_up_call_query)
        follow_up_call = follow_up_call_result.scalar_one_or_none()
        
        if not follow_up_call:
            logger.warning(f"Follow-up call with ID {follow_up_call_id} not found")
            return False
        
        # Delete follow-up call
        delete_query = delete(FollowUpCall).where(FollowUpCall.id == follow_up_call_id)
        await self.session.execute(delete_query)
        await self.session.commit()
        
        return True
    
    async def get_follow_up_calls_by_campaign(
        self, 
        campaign_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get follow-up calls for a campaign with pagination.
        
        Args:
            campaign_id: Campaign ID
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing follow-up calls and pagination info
        """
        logger.info(f"Getting follow-up calls for campaign: {campaign_id}")
        
        # Build query for follow-up calls
        base_query = select(FollowUpCall).where(FollowUpCall.campaign_id == campaign_id)
        
        # Count total follow-up calls
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await self.session.execute(count_query)
        total = total_count.scalar_one()
        
        if total == 0:
            return {
                "follow_up_calls": [],
                "pagination": {
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "pages": 0
                }
            }
        
        # Get follow-up calls with pagination
        offset = (page - 1) * page_size
        follow_up_calls_query = (
            base_query
            .order_by(desc(FollowUpCall.call_date_time))
            .offset(offset)
            .limit(page_size)
        )
        follow_up_calls_result = await self.session.execute(follow_up_calls_query)
        follow_up_calls = follow_up_calls_result.scalars().all()
        
        # Convert to dictionaries
        follow_up_call_data = [follow_up_call.to_dict() for follow_up_call in follow_up_calls]
        
        return {
            "follow_up_calls": follow_up_call_data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
        }
    
    async def get_follow_up_calls_by_lead(
        
        self, 
        lead_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get follow-up calls for a lead with pagination.
        
        Args:
            lead_id: Lead ID
            page: Page number
            page_size: Page size
            
        Returns:
            Dictionary containing follow-up calls and pagination info
        """
        logger.info(f"Getting follow-up calls for lead: {lead_id}")
        
        # Build query for follow-up calls
        base_query = select(FollowUpCall).where(FollowUpCall.lead_id == lead_id)
        
        # Count total follow-up calls
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await self.session.execute(count_query)
        total = total_count.scalar_one()
        
        if total == 0:
            return {
                "follow_up_calls": [],
                "pagination": {
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "pages": 0
                }
            }
        
        # Get follow-up calls with pagination
        offset = (page - 1) * page_size
        follow_up_calls_query = (
            base_query
            .order_by(desc(FollowUpCall.call_date_time))
            .offset(offset)
            .limit(page_size)
        )
        follow_up_calls_result = await self.session.execute(follow_up_calls_query)
        follow_up_calls = follow_up_calls_result.scalars().all()
        
        # Convert to dictionaries
        follow_up_call_data = [follow_up_call.to_dict() for follow_up_call in follow_up_calls]
        
        return {
            "follow_up_calls": follow_up_call_data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
        }

    # Stub implementations for abstract methods we're not using yet
    
    async def get_active_calls(self, gym_id: str) -> List[Dict[str, Any]]:
        """
        Get all active calls for a gym.
        
        Args:
            gym_id: Unique identifier of the gym
            
        Returns:
            List of active call data
        """
        logger.info(f"Getting active calls for gym {gym_id}")
        # Placeholder implementation
        return []
        
    async def get_call_by_external_id(self, external_call_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a call by external call ID.
        
        Args:
            external_call_id: External ID of the call (e.g., from Retell)
        
        Returns:
            Dictionary containing call data, or None if not found
        """
        logger.info(f"Getting call with external ID: {external_call_id}")
        
        # Query call by external_call_id
        call_query = select(CallLog).where(CallLog.external_call_id == external_call_id)
        call_result = await self.session.execute(call_query)
        call = call_result.scalar_one_or_none()
        
        if not call:
            logger.warning(f"No call found with external ID {external_call_id}")
            return None
            
        # Return call data as dictionary
        return call.to_dict()
        
    async def save_call_recording(self, call_id: str, recording_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Save call recording information.
        
        Args:
            call_id: Unique identifier of the call
            recording_data: Dictionary containing recording details
            
        Returns:
            Updated call data if successful, None if call not found
        """
        logger.info(f"Saving recording for call: {call_id}")
        # Placeholder implementation
        return await self.get_call_by_id(call_id)
        
    async def save_call_transcript(self, call_id: str, transcript_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Save call transcript.
        
        Args:
            call_id: Unique identifier of the call
            transcript_data: Dictionary containing transcript details
            
        Returns:
            Updated call data if successful, None if call not found
        """
        logger.info(f"Saving transcript for call: {call_id}")
        # Placeholder implementation
        return await self.get_call_by_id(call_id)
        
    async def update_call_outcome(self, call_id: str, outcome: str) -> Optional[Dict[str, Any]]:
        """
        Update call outcome.
        
        Args:
            call_id: Unique identifier of the call
            outcome: New outcome
            
        Returns:
            Updated call data if successful, None if call not found
        """
        logger.info(f"Updating outcome for call: {call_id}")
        # Placeholder implementation using update_call
        return await self.update_call(call_id, {"call_outcome": outcome})
        
    async def update_call_status(self, call_id: str, status: str) -> Optional[Dict[str, Any]]:
        """
        Update call status.
        
        Args:
            call_id: Unique identifier of the call
            status: New status
            
        Returns:
            Updated call data if successful, None if call not found
        """
        logger.info(f"Updating status for call: {call_id}")
        # Placeholder implementation using update_call
        return await self.update_call(call_id, {"call_status": status})