"""
Celery tasks for report generation and delivery.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio

from backend.celery_app import celery_app
from backend.db.connections.database import get_db_context
from backend.services.reporting.factory import create_reporting_service

logger = logging.getLogger(__name__)


@celery_app.task(name="generate_reports")
def generate_reports() -> Dict[str, Any]:
    """
    Check for scheduled reports and generate them.
    This task should be scheduled to run every minute.
    """
    logger.info("Checking for scheduled reports...")
    
    try:
        # Run the async task using asyncio
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_check_and_schedule_reports())
        
        return {
            "status": "success",
            "reports_scheduled": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking for scheduled reports: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name="process_reports")
def process_reports(limit: int = 10) -> Dict[str, Any]:
    """
    Process pending reports (generate and send).
    This task should be scheduled to run every few minutes.
    
    Args:
        limit: Maximum number of reports to process in one batch.
    """
    logger.info(f"Processing pending reports (limit: {limit})...")
    
    try:
        # Run the async task using asyncio
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_process_pending_reports(limit))
        
        return {
            "status": "success",
            "reports_processed": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing pending reports: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name="generate_daily_report")
def generate_daily_report(branch_id: str, gym_id: str) -> Dict[str, Any]:
    """
    Generate a daily report for a specific branch/gym.
    This can be called manually or scheduled directly.
    
    Args:
        branch_id: The branch ID.
        gym_id: The gym ID.
    """
    logger.info(f"Generating daily report for branch {branch_id}...")
    
    try:
        # Use yesterday's date for the report
        report_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Run the async task using asyncio
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_generate_daily_report(branch_id, gym_id, report_date))
        
        return {
            "status": "success",
            "report_id": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating daily report: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@celery_app.task(name="generate_weekly_report")
def generate_weekly_report(branch_id: str, gym_id: str) -> Dict[str, Any]:
    """
    Generate a weekly report for a specific branch/gym.
    This can be called manually or scheduled directly.
    
    Args:
        branch_id: The branch ID.
        gym_id: The gym ID.
    """
    logger.info(f"Generating weekly report for branch {branch_id}...")
    
    try:
        # Set the date range for the previous week
        now = datetime.now()
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        # Go back to the previous week's Sunday
        days_since_sunday = now.weekday() + 1  # Monday is 0, so Sunday is 6, and +1 to go to previous week
        end_date = end_date - timedelta(days=days_since_sunday)
        start_date = end_date - timedelta(days=6)  # Monday of the previous week
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Run the async task using asyncio
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_generate_weekly_report(branch_id, gym_id, start_date, end_date))
        
        return {
            "status": "success",
            "report_id": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Async helper functions

async def _check_and_schedule_reports() -> int:
    """
    Check for report subscriptions that should be processed at the current time
    and schedule them for generation and delivery.
    """
    async with get_db_context() as session:
        reporting_service = create_reporting_service(session)
        return await reporting_service.check_and_schedule_reports()


async def _process_pending_reports(limit: int = 10) -> int:
    """
    Process pending reports (generate and send).
    """
    async with get_db_context() as session:
        reporting_service = create_reporting_service(session)
        return await reporting_service.process_pending_reports(limit)


async def _generate_daily_report(branch_id: str, gym_id: str, report_date: datetime) -> str:
    """
    Generate a daily report for a specific branch/gym.
    """
    async with get_db_context() as session:
        reporting_service = create_reporting_service(session)
        
        # Generate report data
        report_data = await reporting_service.generate_daily_report(branch_id, gym_id, report_date)
        
        # Create a delivery record
        delivery_data = {
            "report_type": "daily",
            "branch_id": branch_id,
            "gym_id": gym_id,
            "report_data": report_data,
            "report_period_start": report_date,
            "report_period_end": report_date,
            "recipients": [],  # This will be filled in by the admin or API call
            "delivery_status": "generated"
        }
        
        delivery = await reporting_service.report_repository.create_delivery(delivery_data)
        return delivery["id"]


async def _generate_weekly_report(branch_id: str, gym_id: str, start_date: datetime, end_date: datetime) -> str:
    """
    Generate a weekly report for a specific branch/gym.
    """
    async with get_db_context() as session:
        reporting_service = create_reporting_service(session)
        
        # Generate report data
        report_data = await reporting_service.generate_weekly_report(branch_id, gym_id, start_date, end_date)
        
        # Create a delivery record
        delivery_data = {
            "report_type": "weekly",
            "branch_id": branch_id,
            "gym_id": gym_id,
            "report_data": report_data,
            "report_period_start": start_date,
            "report_period_end": end_date,
            "recipients": [],  # This will be filled in by the admin or API call
            "delivery_status": "generated"
        }
        
        delivery = await reporting_service.report_repository.create_delivery(delivery_data)
        return delivery["id"]
