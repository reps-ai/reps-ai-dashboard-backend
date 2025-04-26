"""
Celery task definitions for campaign operations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import asyncio
import json
import subprocess
import os
import sys

from sqlalchemy import text

from backend.celery_app import app
from ...tasks.base import BaseTask
from ...utils.logging.logger import get_logger
from ...db.connections.database import SessionLocal

from .tasks import CampaignSchedulingService
from .campaign_helpers import db_session

# Task constants
TASK_MAX_RETRIES = 3
TASK_DEFAULT_QUEUE = 'campaign_tasks'

# Configure logging
logger = get_logger(__name__)

# Get the absolute path to the subprocess scripts
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SUBPROCESS_SCRIPT = os.path.join(CURRENT_DIR, "schedule_subprocess.py")
ALL_CAMPAIGNS_SUBPROCESS_SCRIPT = os.path.join(CURRENT_DIR, "schedule_all_subprocess.py")

class ScheduleCampaignTask(BaseTask):
    """Task to schedule calls for a specific campaign."""
    
    name = "campaign.schedule_campaign"
    max_retries = TASK_MAX_RETRIES
    queue = TASK_DEFAULT_QUEUE
    service_class = CampaignSchedulingService
    
    def run(self, campaign_id: str, target_date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Schedule calls for a campaign on a specific date.
        
        Args:
            campaign_id: ID of the campaign
            target_date_str: Date to schedule calls for in ISO format (defaults to today)
            
        Returns:
            List of scheduled calls
        """
        logger.info(f"Scheduling calls for campaign {campaign_id} on {target_date_str or 'today'}")
        
        try:
            # Run the scheduling in a subprocess to guarantee clean event loop
            args = [sys.executable, SUBPROCESS_SCRIPT, campaign_id]
            
            if target_date_str:
                args.append(target_date_str)
            
            # Execute the subprocess and capture its output
            logger.info(f"Launching subprocess with args: {args}")
            process = subprocess.Popen(
                args, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Get output with timeout
            stdout, stderr = process.communicate(timeout=180)  # 3 minute timeout
            
            # Check for errors in stderr
            if stderr and process.returncode != 0:
                logger.error(f"Subprocess error: {stderr}")
                raise Exception(f"Subprocess failed: {stderr}")
            
            # Process output - it should be JSON
            try:
                if stdout.strip():
                    result = json.loads(stdout)
                    
                    # Log diagnostics if present
                    if isinstance(result, dict) and 'diagnostics' in result:
                        diagnostics = result.get('diagnostics', {})
                        
                        # Log important information from diagnostics
                        if diagnostics.get('error'):
                            logger.error(f"Subprocess encountered an error: {diagnostics['error']}")
                        
                        if diagnostics.get('warning'):
                            logger.warning(f"Subprocess warning: {diagnostics['warning']}")
                        
                        if 'reason_no_calls' in diagnostics:
                            logger.info(f"Reason no calls were scheduled: {diagnostics['reason_no_calls']}")
                        
                        # Log a summary of the execution
                        logger.info(
                            f"Subprocess execution summary: "
                            f"Campaign '{diagnostics.get('campaign_details', {}).get('name')}', "
                            f"Leads: {diagnostics.get('lead_count', 0)}, "
                            f"Calls scheduled: {diagnostics.get('calls_scheduled', 0)}, "
                            f"Steps completed: {', '.join(diagnostics.get('steps_completed', []))}"
                        )
                        
                        # Extract the actual scheduled calls from the result
                        scheduled_calls = result.get('scheduled_calls', [])
                        logger.info(f"Subprocess completed successfully with {len(scheduled_calls)} calls scheduled")
                        return scheduled_calls
                    else:
                        # Legacy format handling
                        logger.info(f"Subprocess completed successfully with {len(result)} calls scheduled")
                        return result
                else:
                    logger.warning("Subprocess returned empty output")
                    return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse subprocess output: {e}")
                logger.error(f"Raw output: {stdout[:1000]}")  # Log first 1000 chars
                return []
                
        except subprocess.TimeoutExpired:
            logger.error(f"Subprocess timed out for campaign {campaign_id}")
            # Kill the process if it's still running
            if process and process.poll() is None:
                process.kill()
            raise self.retry(
                exc=Exception(f"Subprocess timed out for campaign {campaign_id}"), 
                countdown=60 * 5
            )
        except Exception as e:
            logger.error(f"Error scheduling calls for campaign {campaign_id}: {str(e)}")
            raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes

    # Keep the original method for reference but don't use it
    async def _schedule_with_shared_session(self, campaign_id: str, target_date: date) -> List[Dict[str, Any]]:
        """Schedule calls using a shared session to prevent connection leaks."""
        # ...existing code...


class ScheduleAllCampaignsTask(BaseTask):
    """Task to schedule calls for all active campaigns."""
    
    name = "campaign.schedule_all_campaigns"
    max_retries = TASK_MAX_RETRIES
    queue = TASK_DEFAULT_QUEUE
    service_class = CampaignSchedulingService
    
    def run(self, target_date_str: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Schedule calls for all active campaigns on a specific date.
        
        Args:
            target_date_str: Date to schedule calls for in ISO format (defaults to today)
            
        Returns:
            Dictionary mapping campaign IDs to lists of scheduled calls
        """
        logger.info(f"Scheduling calls for all campaigns on {target_date_str or 'today'}")
        
        try:
            # Run the scheduling in a subprocess to guarantee clean event loop
            args = [sys.executable, ALL_CAMPAIGNS_SUBPROCESS_SCRIPT]
            
            if target_date_str:
                args.append(target_date_str)
            
            # Execute the subprocess and capture its output
            logger.info(f"Launching subprocess with args: {args}")
            process = subprocess.Popen(
                args, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Get output with timeout - allow more time since this processes multiple campaigns
            stdout, stderr = process.communicate(timeout=600)  # 10 minute timeout
            
            # Check for errors in stderr
            if stderr and process.returncode != 0:
                logger.error(f"Subprocess error: {stderr}")
                raise Exception(f"Subprocess failed: {stderr}")
            
            # Process output - it should be JSON
            try:
                if stdout.strip():
                    result = json.loads(stdout)
                    total_calls = sum(len(calls) for calls in result.values())
                    logger.info(f"Subprocess completed successfully with {total_calls} calls scheduled across {len(result)} campaigns")
                    return result
                else:
                    logger.warning("Subprocess returned empty output")
                    return {}
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse subprocess output: {e}")
                logger.error(f"Raw output: {stdout[:1000]}")  # Log first 1000 chars
                return {}
                
        except subprocess.TimeoutExpired:
            logger.error(f"Subprocess timed out for scheduling all campaigns")
            # Kill the process if it's still running
            if process and process.poll() is None:
                process.kill()
            raise self.retry(
                exc=Exception(f"Subprocess timed out for scheduling all campaigns"), 
                countdown=60 * 5
            )
        except Exception as e:
            logger.error(f"Error scheduling calls for all campaigns: {str(e)}")
            raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes


# Create and register tasks with Celery
schedule_campaign_task = app.register_task(ScheduleCampaignTask())
schedule_all_campaigns_task = app.register_task(ScheduleAllCampaignsTask())
