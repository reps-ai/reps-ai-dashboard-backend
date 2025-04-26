"""
Script to update all campaigns with zero frequency to have a valid frequency.
"""
import asyncio
import os
import sys
import json
from sqlalchemy import update, select

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.connections.database import get_db_session
from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign
from contextlib import asynccontextmanager

@asynccontextmanager
async def db_session():
    """Context manager for database sessions."""
    session = await get_db_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def update_campaign_frequencies():
    """Update all campaigns with zero frequency to have a valid frequency."""
    async with db_session() as session:
        # Create default schedule settings
        default_schedule = {
            "max_daily_calls": 3,
            "call_days": ["mon", "tue", "wed", "thu", "fri"]
        }
        
        try:
            # Update campaigns with zero frequency
            # First, fetch all campaigns with frequency = 0
            query = select(FollowUpCampaign.id).where(FollowUpCampaign.frequency == 0)
            result = await session.execute(query)
            campaigns_to_update = result.scalars().all()
            
            if not campaigns_to_update:
                print("No campaigns with zero frequency found.")
                return
                
            print(f"Found {len(campaigns_to_update)} campaigns with zero frequency")
            
            # Update each campaign individually to ensure proper JSON merging
            for campaign_id in campaigns_to_update:
                # Get current campaign data
                query = select(FollowUpCampaign).where(FollowUpCampaign.id == campaign_id)
                result = await session.execute(query)
                campaign = result.scalar_one_or_none()
                
                if not campaign:
                    continue
                    
                # Prepare updated metrics
                current_metrics = campaign.metrics or {}
                if not isinstance(current_metrics, dict):
                    current_metrics = {}
                    
                current_metrics["schedule"] = default_schedule
                
                # Update the campaign
                campaign.frequency = 5
                campaign.metrics = current_metrics
            
            # Commit all changes at once
            await session.commit()
            
            print(f"Updated {len(campaigns_to_update)} campaigns with frequency=5 and schedule settings.")
            
        except Exception as e:
            await session.rollback()
            print(f"Error updating campaigns: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(update_campaign_frequencies())
