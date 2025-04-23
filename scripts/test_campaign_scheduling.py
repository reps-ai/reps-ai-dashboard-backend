"""
Test script for campaign call scheduling.
This script will test scheduling calls for campaigns.
"""
import asyncio
import sys
from datetime import datetime, date, timedelta
import uuid
import os

# Ensure we can import from the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Instead of disabling Redis cache entirely, let's handle errors more gracefully
# by adding a shorter timeout for Redis operations


# Fix imports for the restructured campaign task modules
from backend.tasks.campaign.task_definitions import ScheduleCampaignTask, ScheduleAllCampaignsTask
from backend.tasks.campaign.tasks import CampaignSchedulingService

# Get instances for direct use
campaign_scheduling_service = CampaignSchedulingService()
schedule_calls_for_campaign = campaign_scheduling_service.schedule_calls_for_campaign
schedule_calls_for_all_campaigns = campaign_scheduling_service.schedule_calls_for_all_campaigns

# For Celery task usage
schedule_campaign_task = ScheduleCampaignTask().run
schedule_all_campaigns_task = ScheduleAllCampaignsTask().run

from backend.db.connections.database import get_db_session
from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign
from sqlalchemy import select


async def test_campaign_by_id(campaign_id=None):
    """
    Test scheduling calls for a specific campaign.
    
    Args:
        campaign_id: ID of the campaign to test. If None, will prompt for input.
    """
    if campaign_id is None:
        campaign_id = input("Enter campaign ID: ")
    
    # Get today's date for testing
    today = date.today()
    
    print(f"Testing call scheduling for campaign {campaign_id} on {today}")
    
    try:
        # Get current campaign status
        campaign = await campaign_scheduling_service.get_campaign(campaign_id)
        current_status = campaign.get('campaign_status')
        
        # Check if campaign is in a status that can be scheduled
        if current_status not in ['not_started', 'paused']:
            print(f"Campaign status is '{current_status}'. Only not_started or paused campaigns can be scheduled.")
            proceed = input("Do you want to temporarily set the status to 'not_started' for testing? (y/n): ")
            if proceed.lower() == 'y':
                await campaign_scheduling_service.update_campaign(campaign_id, {'campaign_status': 'not_started'})
                print(f"Temporarily set campaign status to 'not_started' for testing.")
            else:
                print("Test cancelled.")
                return []
        
        # Call the async function directly for testing
        result = await schedule_calls_for_campaign(campaign_id, today)
        print(f"Scheduled {len(result)} calls for campaign {campaign_id}")
        
        # Print each scheduled call
        for i, call in enumerate(result, 1):
            print(f"  Call {i}: Lead {call.get('lead_id')} at {call.get('scheduled_time')}")
        
        return result
    except Exception as e:
        print(f"Error scheduling calls: {str(e)}")
        return []


async def test_all_campaigns():
    """Test scheduling calls for all active campaigns."""
    # Get today's date for testing
    today = date.today()
    
    print(f"Testing scheduling for all active campaigns on {today}")
    
    try:
        # Call the async function directly for testing
        result = await schedule_calls_for_all_campaigns(today)
        
        # Count total calls
        total_calls = sum(len(calls) for calls in result.values())
        
        print(f"Scheduled calls for {len(result)} campaigns:")
        for campaign_id, calls in result.items():
            print(f"  - Campaign {campaign_id}: {len(calls)} calls scheduled")
        
        return result
    except Exception as e:
        print(f"Error scheduling calls: {str(e)}")
        return {}


async def list_campaigns():
    """List all campaigns for testing."""
    session = await get_db_session()
    try:
        # Query all campaigns
        query = select(FollowUpCampaign)
        result = await session.execute(query)
        campaigns = result.scalars().all()
        
        if not campaigns:
            print("No campaigns found in the database.")
            return []
        
        print(f"Found {len(campaigns)} campaigns:")
        for i, campaign in enumerate(campaigns, 1):
            print(f"{i}. ID: {campaign.id} - Name: {campaign.name} - Status: {campaign.campaign_status}")
            print(f"   Frequency: {campaign.frequency} - Call count: {campaign.call_count}")
            
        return campaigns
    except Exception as e:
        print(f"Error listing campaigns: {str(e)}")
        return []
    finally:
        await session.close()


async def menu():
    """Interactive menu for testing campaign scheduling."""
    while True:
        print("\nCampaign Call Scheduling Test")
        print("===========================")
        print("\nSelect a test:")
        print("1. Test specific campaign")
        print("2. Test all campaigns")
        print("3. List campaigns")
        print("4. Exit")
        
        choice = input("Your choice: ")
        
        if choice == "1":
            campaigns = await list_campaigns()
            if campaigns:
                idx = int(input("Enter campaign number: ")) - 1
                if 0 <= idx < len(campaigns):
                    campaign_id = str(campaigns[idx].id)
                    await test_campaign_by_id(campaign_id)
                else:
                    print("Invalid campaign number")
            else:
                campaign_id = input("Enter campaign ID: ")
                await test_campaign_by_id(campaign_id)
                
        elif choice == "2":
            await test_all_campaigns()
            
        elif choice == "3":
            await list_campaigns()
            
        elif choice == "4":
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        asyncio.run(menu())
    except KeyboardInterrupt:
        print("\nExiting...")
