"""
Subprocess script for scheduling calls for campaigns.
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

# Set up detailed logging that writes to stderr
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'campaign_subprocess.log')

# Disable any root loggers that might have been configured elsewhere
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure our own root logger to write to stderr only
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    ]
)

# Avoid loading modules that might configure their own loggers
logger = logging.getLogger("campaign_subprocess")
logger.info(f"=============== SUBPROCESS STARTED WITH ARGS: {sys.argv} ===============")

# Force other modules to use our logger configuration
logging.getLogger("backend").setLevel(logging.DEBUG)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

async def schedule_campaign_calls(
    campaign_id: str, 
    target_date_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Schedule calls for a campaign in a dedicated process with its own event loop.
    
    Args:
        campaign_id: ID of the campaign
        target_date_str: Optional date string in ISO format
        
    Returns:
        Dictionary with scheduling results and diagnostic information
    """
    diagnostics = {
        "start_time": datetime.now().isoformat(),
        "campaign_id": campaign_id,
        "target_date": target_date_str,
        "steps_completed": [],
        "error": None,
        "campaign_details": None,
        "lead_count": 0,
        "calls_scheduled": 0
    }
    
    try:
        logger.info(f"Step 1: Importing dependencies for campaign {campaign_id}")
        diagnostics["steps_completed"].append("imports_started")
        
        # Import services here using absolute imports instead of relative imports
        from backend.db.connections.database import SessionLocal
        from backend.services.campaign.factory import create_campaign_service_async
        from backend.services.call.factory import create_call_service_async
        from backend.tasks.campaign.tasks import CampaignSchedulingService
        from sqlalchemy import text
        
        diagnostics["steps_completed"].append("imports_completed")
        
        # Convert string date to date object if provided
        if target_date_str:
            try:
                target_date = datetime.fromisoformat(target_date_str).date()
            except ValueError:
                logger.error(f"Invalid date format: {target_date_str}. Using today's date.")
                target_date = date.today()
                diagnostics["error"] = f"Invalid date format: {target_date_str}"
        else:
            target_date = date.today()
        
        diagnostics["parsed_date"] = str(target_date)
        logger.info(f"Step 2: Scheduling campaign {campaign_id} for date {target_date}")
        diagnostics["steps_completed"].append("date_parsed")
        
        # Create a new session
        logger.info("Step 3: Creating database session")
        session = SessionLocal()
        diagnostics["steps_completed"].append("session_created")
        
        try:
            # Verify the session is working
            logger.info("Step 4: Testing database connection")
            await session.execute(text("SELECT 1"))
            diagnostics["steps_completed"].append("db_connection_verified")
            
            # Create services with the shared session
            logger.info("Step 5: Creating services")
            campaign_service = await create_campaign_service_async(session=session)
            call_service = await create_call_service_async(session=session)
            diagnostics["steps_completed"].append("services_created")
            
            # Get campaign details for diagnostics
            logger.info(f"Step 6: Fetching campaign details for {campaign_id}")
            try:
                campaign = await campaign_service.get_campaign(campaign_id)
                diagnostics["campaign_details"] = {
                    "name": campaign.get('name'),
                    "status": campaign.get('campaign_status'),
                    "frequency": campaign.get('frequency'),
                    "start_date": str(campaign.get('start_date')),
                    "end_date": str(campaign.get('end_date')),
                }
                
                logger.info(f"Campaign details: {json.dumps(diagnostics['campaign_details'])}")
                
                # Check if campaign is active - log warning but continue execution
                if campaign.get('campaign_status') != 'active':
                    msg = f"Campaign {campaign_id} is not active (status: {campaign.get('campaign_status')})"
                    logger.warning(msg)
                    diagnostics["warning"] = msg
                
                # Check if today is a valid day for this campaign
                metrics = campaign.get('metrics', {})
                if metrics and 'schedule' in metrics:
                    schedule = metrics['schedule']
                    day_of_week = target_date.strftime('%a').lower()  # 'mon', 'tue', etc.
                    call_days = [d.lower() for d in schedule.get('call_days', [])]
                    
                    if day_of_week not in call_days:
                        msg = f"Today ({day_of_week}) is not a scheduled call day for this campaign. Call days: {call_days}"
                        logger.warning(msg)
                        diagnostics["warning"] = msg
                
                diagnostics["steps_completed"].append("campaign_details_retrieved")
            except Exception as e:
                logger.error(f"Error retrieving campaign: {str(e)}")
                logger.error(traceback.format_exc())
                diagnostics["error"] = f"Error retrieving campaign: {str(e)}"
            
            # Get lead information
            logger.info(f"Step 7: Fetching leads for campaign {campaign_id}")
            try:
                leads = await campaign_service.get_campaign_leads(campaign_id)
                lead_count = len(leads)
                diagnostics["lead_count"] = lead_count
                
                logger.info(f"Found {lead_count} leads for campaign {campaign_id}")
                if lead_count == 0:
                    logger.warning(f"No leads found for campaign {campaign_id} - cannot schedule calls")
                    diagnostics["warning"] = "No leads found for campaign"
                else:
                    # Log details about the first few leads for debugging
                    for i, lead in enumerate(leads[:3]):
                        logger.info(f"Lead {i+1}: {lead.get('first_name')} {lead.get('last_name')} - {lead.get('lead_status')}")
                
                diagnostics["steps_completed"].append("leads_retrieved")
            except Exception as e:
                logger.error(f"Error retrieving leads: {str(e)}")
                logger.error(traceback.format_exc())
                diagnostics["error"] = f"Error retrieving leads: {str(e)}"
            
            # Create the scheduling service
            logger.info("Step 8: Creating scheduling service")
            service = CampaignSchedulingService()
            diagnostics["steps_completed"].append("scheduling_service_created")
            
            # Execute the scheduling operation with the shared session
            logger.info(f"Step 9: Executing schedule_calls_for_campaign for {campaign_id}")
            result = await service.schedule_calls_for_campaign(
                campaign_id,
                target_date,
                campaign_service=campaign_service,
                call_service=call_service,
                session=session
            )
            
            call_count = len(result)
            diagnostics["calls_scheduled"] = call_count
            
            # Log scheduling results
            logger.info(f"Step 10: Scheduled {call_count} calls for campaign {campaign_id}")
            
            # Log detailed information about why no calls were scheduled
            if call_count == 0:
                logger.warning("No calls were scheduled. Checking possible reasons...")
                
                # Check if today is a valid call day for the campaign
                if campaign.get('metrics', {}).get('schedule', {}):
                    schedule = campaign.get('metrics', {}).get('schedule', {})
                    day_of_week = target_date.strftime('%a').lower()  # 'mon', 'tue', etc.
                    call_days = [d.lower() for d in schedule.get('call_days', [])]
                    
                    if day_of_week not in call_days:
                        msg = f"Today ({day_of_week}) is not a scheduled call day for this campaign. Call days: {call_days}"
                        logger.warning(msg)
                        diagnostics["reason_no_calls"] = msg
                
                # Check frequency vs already scheduled calls
                scheduled_calls = campaign.get('metrics', {}).get('scheduled_calls', 0)
                frequency = campaign.get('frequency', 0)
                
                if scheduled_calls >= frequency:
                    msg = f"Campaign has reached its frequency limit: {scheduled_calls}/{frequency}"
                    logger.warning(msg)
                    diagnostics["reason_no_calls"] = msg
                
                # Check if last scheduled date is today
                last_scheduled = campaign.get('metrics', {}).get('last_scheduled_date')
                if last_scheduled == str(target_date):
                    msg = f"Calls already scheduled for today ({last_scheduled})"
                    logger.warning(msg)
                    diagnostics["reason_no_calls"] = msg
                
                # If none of the above, it's likely lead qualification issues
                if "reason_no_calls" not in diagnostics:
                    msg = "No leads qualified for calls today - check lead statuses or campaign qualification criteria"
                    logger.warning(msg)
                    diagnostics["reason_no_calls"] = msg
            
            # Commit any pending changes
            await session.commit()
            diagnostics["steps_completed"].append("changes_committed")
            
            # Add diagnosis summary
            diagnostics["success"] = True
            diagnostics["end_time"] = datetime.now().isoformat()
            
            return {
                "scheduled_calls": result,
                "diagnostics": diagnostics
            }
            
        except Exception as e:
            logger.error(f"Error in campaign scheduling: {str(e)}")
            logger.error(traceback.format_exc())
            
            if session:
                await session.rollback()
            
            diagnostics["error"] = str(e)
            diagnostics["traceback"] = traceback.format_exc()
            raise
        finally:
            # Always close the session
            if session:
                try:
                    await session.close()
                    diagnostics["steps_completed"].append("session_closed")
                except Exception as close_error:
                    logger.error(f"Error closing session: {str(close_error)}")
                    diagnostics["error"] = f"Error closing session: {str(close_error)}"
    
    except Exception as e:
        logger.error(f"Fatal error in subprocess: {str(e)}")
        logger.error(traceback.format_exc())
        
        diagnostics["error"] = str(e)
        diagnostics["traceback"] = traceback.format_exc()
        diagnostics["success"] = False
        diagnostics["end_time"] = datetime.now().isoformat()
        
        return {
            "scheduled_calls": [],
            "diagnostics": diagnostics
        }

def run_scheduling(campaign_id: str, target_date_str: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Entry point for subprocess execution.
    
    Args:
        campaign_id: ID of the campaign
        target_date_str: Optional date string in ISO format
        
    Returns:
        JSON-serializable list of scheduled calls
    """
    # Run everything in a new, clean event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(schedule_campaign_calls(campaign_id, target_date_str))
        
        # Convert UUID and datetime objects to strings for JSON serialization
        serializable_result = json.dumps(_make_serializable(result))
        return serializable_result
        
    except Exception as e:
        logger.error(f"Error in subprocess runner: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps([])
    finally:
        # Clean up all resources
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

def _make_serializable(obj):
    """Convert complex types like UUID and datetime to strings for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
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
    arg 1: campaign_id
    arg 2 (optional): target_date_str
    
    It prints the JSON result to stdout for the parent process to capture.
    """
    if len(sys.argv) < 2:
        logger.error("Missing campaign_id parameter")
        # Restore stdout for the JSON output only
        sys.stdout = sys.__stdout__
        print(json.dumps({"error": "Missing campaign_id parameter"}))
        sys.exit(1)
        
    campaign_id = sys.argv[1]
    target_date_str = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Run scheduling and get the result
    result = run_scheduling(campaign_id, target_date_str)
    
    # Restore stdout just for the JSON output
    sys.stdout = sys.__stdout__
    print(result)  # This should be the only thing going to stdout
