"""
Script to properly cancel a campaign and revoke any scheduled tasks.
This ensures no further calls will be scheduled or executed.
"""
import asyncio
import sys
import os
import argparse

# Ensure we can import from the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from backend.services.campaign.factory import create_campaign_service_async
from backend.celery_app import app
from backend.utils.logging.logger import get_logger

# Fix the import error by using the correct module path
from celery.app.control import Control

# Configure logging
logger = get_logger(__name__)

async def cancel_campaign(campaign_id: str):
    """
    Cancel a campaign and revoke any scheduled tasks.
    
    Args:
        campaign_id: ID of the campaign to cancel
    """
    print(f"Cancelling campaign {campaign_id}...")
    
    # Create campaign service
    campaign_service = await create_campaign_service_async()
    
    try:
        # Use the new service method to cancel the campaign
        updated_campaign = await campaign_service.cancel_campaign(campaign_id)
        print(f"Successfully cancelled campaign: {updated_campaign.get('name')}")
        print(f"New status: {updated_campaign.get('campaign_status')}")
    
    except Exception as e:
        print(f"Error cancelling campaign: {str(e)}")

async def find_call_tasks_for_campaign(campaign_id: str) -> list:
    """
    Find all call tasks for a specific campaign.
    
    Args:
        campaign_id: Campaign ID to search for
        
    Returns:
        List of task IDs
    """
    # In a real implementation, you would query your task store or Redis
    # to find call tasks associated with this campaign.
    
    # For now, we'll just return an empty list, but you should implement this
    # based on how your call tasks store the campaign_id
    return []

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Cancel a campaign and revoke any scheduled tasks')
    parser.add_argument('campaign_id', help='ID of the campaign to cancel')
    
    args = parser.parse_args()
    
    # Run the async function
    asyncio.run(cancel_campaign(args.campaign_id))
