"""
Subprocess script for scheduling calls for all active campaigns.
This is launched as a separate process to avoid event loop closure issues.
"""
import asyncio
import json
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import traceback

# Redirect all stdout to stderr immediately to prevent any interference
sys.stdout = sys.stderr

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Configure logging to write to stderr
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'campaign_all_subprocess.log')

# Disable any root loggers that might have been configured elsewhere
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure our own root logger to write to stderr only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    ]
)

# Force other modules to use our logger configuration
logging.getLogger("backend").setLevel(logging.DEBUG)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

logger = logging.getLogger("campaign_all_subprocess")
logger.info(f"=============== ALL CAMPAIGNS SUBPROCESS STARTED WITH ARGS: {sys.argv} ===============")

async def schedule_all_campaign_calls(target_date_str: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Schedule calls for all active campaigns in a dedicated process with its own event loop.
    
    Args:
        target_date_str: Optional date string in ISO format
        
    Returns:
        Dictionary mapping campaign IDs to lists of scheduled calls
    """
    try:
        # Import services here using absolute imports
        from backend.db.connections.database import SessionLocal
        from backend.services.campaign.factory import create_campaign_service_async
        from backend.tasks.campaign.tasks import CampaignSchedulingService
        from sqlalchemy import text
        
        # Convert string date to date object if provided
        if target_date_str:
            try:
                target_date = datetime.fromisoformat(target_date_str).date()
            except ValueError:
                logger.error(f"Invalid date format: {target_date_str}. Using today's date.")
                target_date = date.today()
        else:
            target_date = date.today()
            
        logger.info(f"Scheduling all active campaigns for date {target_date}")
        
        # Create a new session
        session = SessionLocal()
        
        try:
            # Verify the session is working
            await session.execute(text("SELECT 1"))
            
            # Create campaign service
            campaign_service = await create_campaign_service_async(session=session)
            
            # Get all active campaigns directly from the repository
            try:
                # Get active campaigns for the target date
                from ...db.repositories.campaign import create_campaign_repository
                campaign_repo = await create_campaign_repository(session)
                active_campaigns = await campaign_repo.get_campaigns_for_date(target_date)
                
                logger.info(f"Found {len(active_campaigns)} active campaigns for date {target_date}")
                
                # Log campaign details
                for i, campaign in enumerate(active_campaigns):
                    campaign_id = campaign.get('id')
                    logger.info(f"Campaign {i+1}/{len(active_campaigns)}: ID={campaign_id}, "
                              f"Name={campaign.get('name')}, Status={campaign.get('campaign_status')}")
                    
                    # Get lead count for this campaign for better diagnostics
                    try:
                        leads = await campaign_service.get_campaign_leads(campaign_id)
                        lead_count = len(leads)
                        logger.info(f"Campaign {campaign_id} has {lead_count} associated leads")
                        if lead_count == 0:
                            logger.warning(f"Campaign {campaign_id} has no leads - will not schedule any calls")
                    except Exception as e:
                        logger.error(f"Error getting leads for campaign {campaign_id}: {str(e)}")
                
                if len(active_campaigns) == 0:
                    logger.warning("No active campaigns found, will not schedule any calls")
                    
            except Exception as e:
                logger.error(f"Error retrieving active campaigns: {str(e)}")
                logger.error(traceback.format_exc())
            
            # Create the scheduling service
            service = CampaignSchedulingService()
            
            # Execute the scheduling operation for all campaigns
            logger.info(f"Executing schedule_calls_for_all_campaigns for date {target_date}")
            result = await service.schedule_calls_for_all_campaigns(
                target_date=target_date,
                get_session=lambda: session  # Pass a function that returns the session
            )
            
            # Log scheduling results
            total_calls = sum(len(calls) for campaign_id, calls in result.items())
            logger.info(f"Scheduled {total_calls} calls across {len(result)} campaigns")
            
            # Log details for each campaign
            for campaign_id, calls in result.items():
                logger.info(f"Campaign {campaign_id}: scheduled {len(calls)} calls")
                if len(calls) == 0:
                    logger.warning(f"No calls were scheduled for campaign {campaign_id}.")
            
            if total_calls == 0:
                logger.warning("No calls were scheduled for any campaign. This could be due to: "
                              "1. No active campaigns with associated leads "
                              "2. All campaigns already reached their frequency limit "
                              "3. No leads qualified for calls today")
            
            # Commit any pending changes
            await session.commit()
            return result
            
        except Exception as e:
            logger.error(f"Error in subprocess scheduling all campaigns: {str(e)}")
            logger.error(traceback.format_exc())
            if session:
                await session.rollback()
            raise
        finally:
            # Always close the session
            if session:
                await session.close()
    
    except Exception as e:
        logger.error(f"Fatal error in subprocess: {str(e)}")
        logger.error(traceback.format_exc())
        return {}

def run_all_scheduling(target_date_str: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Entry point for subprocess execution.
    
    Args:
        target_date_str: Optional date string in ISO format
        
    Returns:
        JSON-serializable dict mapping campaign IDs to lists of scheduled calls
    """
    # Run everything in a new, clean event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(schedule_all_campaign_calls(target_date_str))
        
        # Convert UUID and datetime objects to strings for JSON serialization
        serializable_result = json.dumps(_make_serializable(result))
        return serializable_result
        
    except Exception as e:
        logger.error(f"Error in subprocess runner: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({})
    finally:
        # Clean up all resources
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

def _make_serializable(obj):
    """Convert complex types like UUID and datetime to strings for JSON serialization."""
    if isinstance(obj, dict):
        return {str(k): _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_serializable(i) for i in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif hasattr(obj, 'hex'):  # UUID objects have a hex attribute
        return str(obj)
    else:
        return obj

if __name__ == "__main__":
    """
    When executed directly, this script expects:
    arg 1 (optional): target_date_str
    
    It prints the JSON result to stdout for the parent process to capture.
    """
    target_date_str = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run and get result
    result = run_all_scheduling(target_date_str)
    
    # Restore stdout just for the JSON output
    sys.stdout = sys.__stdout__
    print(result)  # This should be the only thing going to stdout
