"""
PostgreSQL implementation of the campaign repository.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from ..campaign_repository import CampaignRepository
from ....models.campaign import Campaign
from ....models.campaign_lead import CampaignLead
from ....models.campaign_schedule import CampaignSchedule


class PostgresCampaignRepository(CampaignRepository):
    """
    PostgreSQL implementation of campaign repository operations.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new campaign with scheduling parameters."""
        # Create campaign record
        campaign = Campaign(**campaign_data)
        self.session.add(campaign)
        await self.session.flush()

        # If schedule data is provided, create schedule
        if schedule_data := campaign_data.get('schedule'):
            schedule = CampaignSchedule(
                campaign_id=campaign.id,
                **schedule_data
            )
            self.session.add(schedule)
            await self.session.flush()

        await self.session.commit()
        return campaign.to_dict()

    async def get_campaign_by_id(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign details by ID."""
        query = select(Campaign).where(Campaign.id == campaign_id)
        result = await self.session.execute(query)
        if campaign := result.scalar_one_or_none():
            return campaign.to_dict()
        return None

    async def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update campaign details."""
        query = (
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(**campaign_data)
            .returning(Campaign)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        if campaign := result.scalar_one_or_none():
            return campaign.to_dict()
        return None

    async def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign."""
        query = delete(Campaign).where(Campaign.id == campaign_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def get_active_campaigns(self, gym_id: str) -> List[Dict[str, Any]]:
        """Get all active campaigns for a gym."""
        query = (
            select(Campaign)
            .where(Campaign.gym_id == gym_id)
            .where(Campaign.is_active == True)
        )
        result = await self.session.execute(query)
        return [campaign.to_dict() for campaign in result.scalars().all()]

    async def get_campaigns_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get campaigns scheduled for a specific date."""
        query = (
            select(Campaign)
            .join(CampaignSchedule)
            .where(CampaignSchedule.start_date <= target_date)
            .where(CampaignSchedule.end_date >= target_date)
        )
        result = await self.session.execute(query)
        return [campaign.to_dict() for campaign in result.scalars().all()]

    async def update_campaign_metrics(self, campaign_id: str, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update campaign metrics."""
        query = (
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(metrics=metrics)
            .returning(Campaign)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        if campaign := result.scalar_one_or_none():
            return campaign.to_dict()
        return None

    async def get_campaign_leads(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get all leads associated with a campaign."""
        query = (
            select(CampaignLead)
            .where(CampaignLead.campaign_id == campaign_id)
        )
        result = await self.session.execute(query)
        return [lead.to_dict() for lead in result.scalars().all()]

    async def add_leads_to_campaign(self, campaign_id: str, lead_ids: List[str]) -> bool:
        """Add leads to a campaign."""
        campaign_leads = [
            CampaignLead(campaign_id=campaign_id, lead_id=lead_id)
            for lead_id in lead_ids
        ]
        self.session.add_all(campaign_leads)
        await self.session.commit()
        return True

    async def remove_leads_from_campaign(self, campaign_id: str, lead_ids: List[str]) -> bool:
        """Remove leads from a campaign."""
        query = (
            delete(CampaignLead)
            .where(CampaignLead.campaign_id == campaign_id)
            .where(CampaignLead.lead_id.in_(lead_ids))
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def get_campaign_schedule(self, campaign_id: str) -> Dict[str, Any]:
        """Get the calling schedule for a campaign."""
        query = (
            select(CampaignSchedule)
            .where(CampaignSchedule.campaign_id == campaign_id)
        )
        result = await self.session.execute(query)
        if schedule := result.scalar_one_or_none():
            return schedule.to_dict()
        return {}

    async def update_campaign_schedule(self, campaign_id: str, schedule_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update the calling schedule for a campaign."""
        query = (
            update(CampaignSchedule)
            .where(CampaignSchedule.campaign_id == campaign_id)
            .values(**schedule_data)
            .returning(CampaignSchedule)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        if schedule := result.scalar_one_or_none():
            return schedule.to_dict()
        return None