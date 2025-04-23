"""
Script to fix campaign frequencies that are showing up as 0 in the database.
This script directly updates the database to ensure all campaigns have a non-zero frequency.
"""
import asyncio
import sys
import os
from datetime import datetime

# Ensure we can import from the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from backend.db.connections.database import get_db_session
from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign
from sqlalchemy import select, update, text

async def fix_campaign_frequencies():
    """Fix all campaigns with zero frequency by setting them to 5."""
    print("Fixing campaign frequencies that are set to 0...")
    
    session = await get_db_session()
    try:
        # First, let's inspect the actual values in the database
        query = select(FollowUpCampaign.id, FollowUpCampaign.name, FollowUpCampaign.frequency)
        result = await session.execute(query)
        campaigns = result.all()
        
        print(f"Found {len(campaigns)} campaigns:")
        for campaign in campaigns:
            print(f"ID: {campaign[0]} - Name: {campaign[1]} - Frequency: {campaign[2]}")
        
        # Now let's update all campaigns with frequency = 0
        zero_freq_query = select(FollowUpCampaign).where(FollowUpCampaign.frequency == 0)
        zero_freq_result = await session.execute(zero_freq_query)
        zero_freq_campaigns = zero_freq_result.scalars().all()
        
        print(f"\nFound {len(zero_freq_campaigns)} campaigns with zero frequency:")
        for campaign in zero_freq_campaigns:
            print(f"Updating campaign {campaign.id} - {campaign.name} from frequency {campaign.frequency} to 5")
            
            # Direct update of the campaign frequency
            campaign.frequency = 5
            
            # Also ensure metrics has a schedule with call_days for every day
            metrics = campaign.metrics or {}
            if "schedule" not in metrics:
                metrics["schedule"] = {}
            
            # Set call_days to include all days of the week
            metrics["schedule"]["call_days"] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            
            # Set max_daily_calls to a reasonable value if not set
            if "max_daily_calls" not in metrics["schedule"]:
                metrics["schedule"]["max_daily_calls"] = 5
                
            campaign.metrics = metrics
            
        # Direct update using SQL for all campaigns at once (alternative approach)
        # This is more efficient but we already updated the objects above
        # update_stmt = update(FollowUpCampaign).where(FollowUpCampaign.frequency == 0).values(frequency=5)
        # await session.execute(update_stmt)
        
        # Commit all changes
        await session.commit()
        print("\nSuccessfully updated all campaigns with zero frequency to 5")
        
        # Verify the changes
        verify_query = select(FollowUpCampaign.id, FollowUpCampaign.name, FollowUpCampaign.frequency)
        verify_result = await session.execute(verify_query)
        updated_campaigns = verify_result.all()
        
        print("\nVerified campaign frequencies:")
        for campaign in updated_campaigns:
            print(f"ID: {campaign[0]} - Name: {campaign[1]} - Frequency: {campaign[2]}")
            
        # Check if any still have frequency 0
        zero_count = await session.execute(
            select(text("COUNT(*)")).select_from(FollowUpCampaign).where(FollowUpCampaign.frequency == 0)
        )
        count = zero_count.scalar_one()
        
        if count > 0:
            print(f"\nWARNING: {count} campaigns still have frequency 0!")
        else:
            print("\nAll campaigns now have a non-zero frequency!")
        
    except Exception as e:
        print(f"Error fixing campaign frequencies: {str(e)}")
        await session.rollback()
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(fix_campaign_frequencies())
