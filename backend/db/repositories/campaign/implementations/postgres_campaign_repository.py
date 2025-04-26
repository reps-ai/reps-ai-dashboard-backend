"""
PostgreSQL implementation of the campaign repository.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, and_, or_, func
import json

from ..campaign_repository import CampaignRepository
from ....models.campaign.follow_up_campaign import FollowUpCampaign
from ....models.lead.lead import Lead

class PostgresCampaignRepository(CampaignRepository):
    """
    PostgreSQL implementation of campaign repository operations.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new campaign with scheduling parameters."""
        # Ensure metrics is present and is a dict (JSONB column)
        if "metrics" not in campaign_data or campaign_data["metrics"] is None:
            campaign_data["metrics"] = {}
        # Create campaign record
        campaign = FollowUpCampaign(**campaign_data)
        self.session.add(campaign)
        await self.session.commit()
        return campaign.to_dict()

    async def get_campaign_by_id(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign details by ID."""
        query = select(FollowUpCampaign).where(FollowUpCampaign.id == campaign_id)
        result = await self.session.execute(query)
        if campaign := result.scalar_one_or_none():
            return campaign.to_dict()
        return None

    async def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update campaign details."""
        # Ensure metrics is present and is a dict if being updated
        if "metrics" in campaign_data and campaign_data["metrics"] is None:
            campaign_data["metrics"] = {}
        query = (
            update(FollowUpCampaign)
            .where(FollowUpCampaign.id == campaign_id)
            .values(**campaign_data)
            .returning(FollowUpCampaign)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        if campaign := result.scalar_one_or_none():
            return campaign.to_dict()
        return None

    async def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign."""
        query = delete(FollowUpCampaign).where(FollowUpCampaign.id == campaign_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def get_active_campaigns_by_branch(self, branch_id: str) -> List[Dict[str, Any]]:
        """Get all active campaigns for a branch."""
        # Since there's no is_active field, we need to filter by date range
        current_date = datetime.now().date()
        
        query = (
            select(FollowUpCampaign)
            .where(FollowUpCampaign.branch_id == branch_id)
            .where(
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
        )
        result = await self.session.execute(query)
        return [campaign.to_dict() for campaign in result.scalars().all()]

    async def get_active_campaigns(self, branch_id: str) -> List[Dict[str, Any]]:
        """Alias for get_active_campaigns_by_branch for backward compatibility."""
        return await self.get_active_campaigns_by_branch(branch_id)

    async def get_campaigns_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get campaigns scheduled for a specific date."""
        current_date = datetime.now().date()
        
        query = (
            select(FollowUpCampaign)
            .where(
                and_(
                    or_(
                        FollowUpCampaign.start_date == None,
                        FollowUpCampaign.start_date <= target_date
                    ),
                    or_(
                        FollowUpCampaign.end_date == None,
                        FollowUpCampaign.end_date >= target_date
                    )
                )
            )
        )
        result = await self.session.execute(query)
        return [campaign.to_dict() for campaign in result.scalars().all()]

    async def update_campaign_metrics(self, campaign_id: str, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update campaign metrics."""
        query = (
            update(FollowUpCampaign)
            .where(FollowUpCampaign.id == campaign_id)
            .values(metrics=metrics)
            .returning(FollowUpCampaign)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        if campaign := result.scalar_one_or_none():
            return campaign.to_dict()
        return None

    async def get_campaign_leads(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get all leads associated with a campaign."""
        # Query leads with the campaign_id field
        query = select(Lead).where(Lead.campaign_id == campaign_id)
        result = await self.session.execute(query)
        leads = result.scalars().all()
        
        # Convert to dictionaries
        return [lead.to_dict() for lead in leads]

    async def increment_call_count(self, campaign_id: str, count: int = 1) -> Optional[Dict[str, Any]]:
        """Increment the call count for a campaign."""
        query = (
            update(FollowUpCampaign)
            .where(FollowUpCampaign.id == campaign_id)
            .values(call_count=FollowUpCampaign.call_count + count)
            .returning(FollowUpCampaign)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        if campaign := result.scalar_one_or_none():
            return campaign.to_dict()
        return None

    async def get_campaign_schedule(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get campaign schedule information.
        This is currently stored in the metrics JSON field.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dictionary containing schedule information or None if not found
        """
        # Get the campaign
        campaign = await self.get_campaign_by_id(campaign_id)
        if not campaign:
            return None
            
        # Extract schedule information from metrics
        metrics = campaign.get('metrics', {})
        if not metrics:
            return {}
            
        # Return schedule data if it exists
        schedule_data = metrics.get('schedule', {})
        return schedule_data

    async def update_campaign_schedule(self, campaign_id: str, schedule_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update campaign schedule information.
        This is currently stored in the metrics JSON field.
        
        Args:
            campaign_id: ID of the campaign
            schedule_data: Dictionary containing updated schedule information
            
        Returns:
            Updated schedule information or None if campaign not found
        """
        # Get the campaign
        campaign = await self.get_campaign_by_id(campaign_id)
        if not campaign:
            return None
            
        # Get current metrics or initialize if not exists
        metrics = campaign.get('metrics', {})
        if not metrics:
            metrics = {}
            
        # Update schedule information
        metrics['schedule'] = schedule_data
        
        # Update the campaign
        query = (
            update(FollowUpCampaign)
            .where(FollowUpCampaign.id == campaign_id)
            .values(metrics=metrics)
            .returning(FollowUpCampaign)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        
        if updated_campaign := result.scalar_one_or_none():
            return updated_campaign.metrics.get('schedule', {}) if updated_campaign.metrics else {}
            
        return None

    async def add_leads_to_campaign(self, campaign_id: str, lead_ids: List[str]) -> bool:
        """
        Add leads to a campaign.
        
        Args:
            campaign_id: ID of the campaign
            lead_ids: List of lead IDs to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if campaign exists
            query = select(FollowUpCampaign).where(FollowUpCampaign.id == campaign_id)
            result = await self.session.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return False
                
            # Update each lead to add them to the campaign
            for lead_id in lead_ids:
                query = (
                    update(Lead)
                    .where(Lead.id == lead_id)
                    .values(campaign_id=campaign_id)
                )
                await self.session.execute(query)
                
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Error adding leads to campaign: {str(e)}")
            return False

    async def remove_leads_from_campaign(self, campaign_id: str, lead_ids: List[str]) -> bool:
        """
        Remove leads from a campaign.
        
        Args:
            campaign_id: ID of the campaign
            lead_ids: List of lead IDs to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if campaign exists
            query = select(FollowUpCampaign).where(FollowUpCampaign.id == campaign_id)
            result = await self.session.execute(query)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return False
                
            # Update each lead to remove them from the campaign
            for lead_id in lead_ids:
                query = (
                    update(Lead)
                    .where(and_(
                        Lead.id == lead_id,
                        Lead.campaign_id == campaign_id
                    ))
                    .values(campaign_id=None)
                )
                await self.session.execute(query)
                
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Error removing leads from campaign: {str(e)}")
            return False

    async def get_call_ids_for_campaign(self, campaign_id: str) -> List[str]:
        """
        Get IDs of all calls associated with a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            List of call IDs
        """
        from ....models.call.call_log import CallLog
        
        query = select(CallLog.id).where(CallLog.campaign_id == campaign_id)
        result = await self.session.execute(query)
        return [str(row[0]) for row in result.all()]

    async def get_campaigns_by_branch(self, branch_id: str) -> List[Dict[str, Any]]:
        """Get all campaigns for a branch (no date filtering)."""
        query = select(FollowUpCampaign).where(FollowUpCampaign.branch_id == branch_id)
        result = await self.session.execute(query)
        return [campaign.to_dict() for campaign in result.scalars().all()]

    async def filter_campaigns_by_branch(self, branch_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get all campaigns for a branch with SQL-level filtering.
        Supported filters: status, search, date (start_date/end_date overlap), campaign_status, name, etc.
        """
        query = select(FollowUpCampaign).where(FollowUpCampaign.branch_id == branch_id)
        if filters:
            if "status" in filters:
                query = query.where(FollowUpCampaign.campaign_status == filters["status"])
            if "campaign_status" in filters:
                query = query.where(FollowUpCampaign.campaign_status == filters["campaign_status"])
            if "search" in filters:
                search = f"%{filters['search']}%"
                query = query.where(FollowUpCampaign.name.ilike(search))
            if "date" in filters:
                target_date = filters["date"]
                query = query.where(
                    or_(
                        FollowUpCampaign.start_date == None,
                        FollowUpCampaign.start_date <= target_date
                    ),
                    or_(
                        FollowUpCampaign.end_date == None,
                        FollowUpCampaign.end_date >= target_date
                    )
                )
            if "name" in filters:
                query = query.where(FollowUpCampaign.name == filters["name"])
            # Add more filters as needed

        result = await self.session.execute(query)
        return [campaign.to_dict() for campaign in result.scalars().all()]