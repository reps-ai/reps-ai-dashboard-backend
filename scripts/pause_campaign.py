"""
Script to pause or cancel an active campaign.
This stops any further calls from being scheduled.
"""
import asyncio
import sys
import os
import argparse

# Ensure we can import from the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from backend.services.campaign.factory import create_campaign_service_async

async def pause_campaign(campaign_id: str, cancel: bool = False):
    """
    Pause or cancel a campaign.
    
    Args:
        campaign_id: ID of the campaign to pause
        cancel: If True, cancel the campaign instead of pausing it
    """
    action = "Cancelling" if cancel else "Pausing"
    print(f"{action} campaign {campaign_id}...")
    
    # Create campaign service
    campaign_service = await create_campaign_service_async()
    
    try:
        # Get campaign details first
        campaign = await campaign_service.get_campaign(campaign_id)
        if not campaign:
            print(f"Campaign {campaign_id} not found")
            return
            
        print(f"Found campaign: {campaign.get('name')} (Status: {campaign.get('campaign_status')})")
        
        # Set new status
        new_status = 'cancelled' if cancel else 'paused'
        
        # Update campaign status
        updated_campaign = await campaign_service.update_campaign(campaign_id, {
            'campaign_status': new_status
        })
        
        print(f"Successfully {action.lower()}d campaign. New status: {updated_campaign.get('campaign_status')}")
    
    except Exception as e:
        print(f"Error {action.lower()} campaign: {str(e)}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Pause or cancel a campaign')
    parser.add_argument('campaign_id', help='ID of the campaign to pause or cancel')
    parser.add_argument('--cancel', action='store_true', help='Cancel the campaign instead of pausing it')
    
    args = parser.parse_args()
    
    # Run the async function
    asyncio.run(pause_campaign(args.campaign_id, args.cancel))
