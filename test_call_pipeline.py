#!/usr/bin/env python
"""
Test script for the lead update pipeline after a call.
Run this script with a valid external_call_id to test the full process.
"""
import asyncio
import sys
from uuid import UUID
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_lead_update_pipeline(external_call_id: str):
    """Test the lead update pipeline with an existing call ID."""
    try:
        # Import the necessary components
        from backend.tasks.call.tasks import ProcessCompletedCallTask
        from backend.db.connections.database import get_db_session
        from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository

        logger.info(f"Testing lead update pipeline with call ID: {external_call_id}")
        
        # Create task instance
        task = ProcessCompletedCallTask()
        
        # 1. Verify call exists in database
        session = await get_db_session()
        try:
            call_repo = PostgresCallRepository(session)
            call = await call_repo.get_call_by_external_id(external_call_id)
            
            if not call:
                logger.error(f"Call with external ID {external_call_id} not found in database")
                return
                
            logger.info(f"Found call: {call.get('id')}, Lead ID: {call.get('lead_id')}")
            logger.info(f"Current call data - Outcome: {call.get('outcome')}, Summary: {call.get('summary', '')[:50]}...")
            
            # 2. Record lead status before update
            lead_id = call.get('lead_id')
            if not lead_id:
                logger.error("Call has no associated lead ID")
                return
                
            from backend.db.repositories.lead.implementations.postgres_lead_repository import PostgresLeadRepository
            lead_repo = PostgresLeadRepository(session)
            lead_before = await lead_repo.get_lead_by_id(str(lead_id))
            
            if not lead_before:
                logger.error(f"Lead with ID {lead_id} not found")
                return
                
            logger.info(f"Lead before update - Status: {lead_before.get('lead_status')}, "
                      f"Last Summary: {lead_before.get('last_conversation_summary', '')[:50]}...")
            
            # 3. Run the task synchronously (not as a background job)
            logger.info("Executing process_completed_call task...")
            result = await task._process_call(external_call_id)
            logger.info(f"Task result: {result}")
            
            # 4. Check lead status after update
            lead_after = await lead_repo.get_lead_by_id(str(lead_id))
            logger.info(f"Lead after update - Status: {lead_after.get('lead_status')}, "
                      f"Last Summary: {lead_after.get('last_conversation_summary', '')[:50]}...")
            
            # 5. Verify changes
            if lead_before.get('lead_status') != lead_after.get('lead_status'):
                logger.info(f"✅ Lead status changed: {lead_before.get('lead_status')} → {lead_after.get('lead_status')}")
            else:
                logger.warning("❌ Lead status did not change")
                
            if lead_before.get('last_conversation_summary') != lead_after.get('last_conversation_summary'):
                logger.info("✅ Last conversation summary was updated")
            else:
                logger.warning("❌ Last conversation summary did not change")
                
            logger.info("Test completed")
            
        finally:
            await session.close()
            
    except Exception as e:
        logger.error(f"Error testing pipeline: {str(e)}", exc_info=True)

def trigger_background_task(external_call_id: str):
    """Trigger the background task through Celery."""
    try:
        # Import and directly invoke the Celery task
        from backend.celery_app import app
        
        # Make sure Redis URL is set
        if not os.environ.get('REDIS_URL') and not os.environ.get('CELERY_BROKER_URL'):
            os.environ['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
            os.environ['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
            
        logger.info(f"Triggering background task for call ID: {external_call_id}")
        
        # Use the app.send_task method to ensure we're using the registered task
        task = app.send_task(
            'backend.tasks.call.process_completed_call',
            args=[external_call_id],
            queue='call_tasks'
        )
        
        logger.info(f"Task triggered with ID: {task.id}")
        logger.info("Task is running in the background. Check celery logs for results.")
        
    except Exception as e:
        logger.error(f"Error triggering background task: {str(e)}", exc_info=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_call_pipeline.py <external_call_id> [--background]")
        sys.exit(1)
        
    external_call_id = sys.argv[1]
    use_background = len(sys.argv) > 2 and sys.argv[2] == "--background"
    
    if use_background:
        # Trigger task through Celery
        trigger_background_task(external_call_id)
    else:
        # Run task synchronously
        asyncio.run(test_lead_update_pipeline(external_call_id)) 