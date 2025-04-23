"""
Script to update all campaign schedules to include every day of the week.
This ensures campaigns can be called on any day during testing.
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
from sqlalchemy import select, update

async def update_all_campaign_schedules():
    """Update all campaign schedules to include every day of the week."""
    print("Updating campaign schedules to include all days of the week...")
    
    session = await get_db_session()
    try:
        # Query all campaigns
        query = select(FollowUpCampaign)
        result = await session.execute(query)
        campaigns = result.scalars().all()
        
        if not campaigns:
            print("No campaigns found in the database.")
            return
        
        print(f"Found {len(campaigns)} campaigns to update")
        
        # Update each campaign
        for campaign in campaigns:
            try:
                # Get current metrics or initialize if not exists
                metrics = campaign.metrics or {}
                
                # Initialize schedule if not exists
                if "schedule" not in metrics:
                    metrics["schedule"] = {}
                
                # Set call_days to include all days of the week
                metrics["schedule"]["call_days"] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                
                # Set max_daily_calls to a reasonable value if not set
                if "max_daily_calls" not in metrics["schedule"]:
                    metrics["schedule"]["max_daily_calls"] = 5
                
                # Update the campaign's metrics JSON field
                campaign.metrics = metrics
                
                # IMPORTANT: Fix any campaigns with zero frequency
                # This fixes the discrepancy between display and actual stored value
                if campaign.frequency == 0:
                    print(f"Campaign {campaign.id} has frequency=0, updating to 5")
                    campaign.frequency = 5
                
                # Log the update
                print(f"Updated campaign {campaign.id} - {campaign.name}")
                
            except Exception as e:
                print(f"Error updating campaign {campaign.id}: {str(e)}")
        
        # Commit all changes
        await session.commit()
        print("Successfully updated all campaign schedules")
        
    except Exception as e:
        print(f"Error updating campaign schedules: {str(e)}")
        await session.rollback()
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(update_all_campaign_schedules())
