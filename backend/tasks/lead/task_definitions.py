"""
Celery tasks for lead processing operations.

This module defines background tasks for lead-related operations using Celery.
Each task is designed to work asynchronously with proper error handling and retry logic.

Tasks defined:
- update_lead: Update lead details
- update_lead_after_call: Update lead information after a call
- qualify_lead: Update lead qualification status
- add_tags_to_lead: Add tags to a lead
- update_lead_batch: Update multiple leads at once
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio
import logging

from backend.celery_app import app
from backend.services.lead.implementation import DefaultLeadService
from backend.db.repositories.lead.implementations import PostgresLeadRepository
from backend.db.connections.database import get_db
from backend.utils.logging.logger import get_logger

logger = get_logger(__name__)

# Configure task-specific settings
TASK_DEFAULT_QUEUE = 'lead_queue'
TASK_DEFAULT_RETRY_DELAY = 5  # seconds
TASK_MAX_RETRIES = 3

@app.task(
    name='lead.update_lead',
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    queue=TASK_DEFAULT_QUEUE
)
def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update lead information as a background task.
    
    Args:
        lead_id: ID of the lead to update
        lead_data: Dictionary containing updated lead information
            
    Returns:
        Dictionary containing the updated lead details
    """
    logger.info(f"Background task: updating lead {lead_id}")
    
    try:
        # Create an async event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Use a try/finally to ensure the loop gets closed
        try:
            # Get database session using context manager
            async def _update_lead():
                async with get_db() as session:
                    # Create service instance with proper repository
                    lead_repository = PostgresLeadRepository(session)
                    lead_service = DefaultLeadService(lead_repository)
                    
                    # Set updated_at timestamp if not provided
                    if "updated_at" not in lead_data:
                        lead_data["updated_at"] = datetime.now().isoformat()
                    
                    # Call the service method (without background task flag to avoid recursion)
                    result = await lead_service.update_lead(lead_id, lead_data)
                    return result
            
            # Run the async function in the event loop
            result = loop.run_until_complete(_update_lead())
            logger.info(f"Successfully updated lead: {lead_id}")
            return result
            
        finally:
            # Clean up the event loop
            loop.close()
    
    except Exception as e:
        logger.error(f"Error updating lead {lead_id}: {str(e)}")
        # Retry with exponential backoff
        self.retry(exc=e, countdown=TASK_DEFAULT_RETRY_DELAY * (2 ** self.request.retries))


@app.task(
    name='lead.update_lead_after_call',
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    queue=TASK_DEFAULT_QUEUE
)
def update_lead_after_call(self, lead_id: str, call_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update lead information after a call as a background task.
    
    Args:
        lead_id: ID of the lead
        call_data: Dictionary containing call information
                
    Returns:
        Dictionary containing the updated lead details
    """
    logger.info(f"Background task: updating lead {lead_id} after call")
    
    try:
        # Create an async event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Use a try/finally to ensure the loop gets closed
        try:
            # Get database session using context manager
            async def _update_lead_after_call():
                async with get_db() as session:
                    # Create service instance with proper repository
                    lead_repository = PostgresLeadRepository(session)
                    lead_service = DefaultLeadService(lead_repository)
                    
                    # Call the service method (without background task flag to avoid recursion)
                    result = await lead_service.update_lead_after_call(lead_id, call_data)
                    return result
            
            # Run the async function in the event loop
            result = loop.run_until_complete(_update_lead_after_call())
            logger.info(f"Successfully updated lead after call: {lead_id}")
            return result
            
        finally:
            # Clean up the event loop
            loop.close()
    
    except Exception as e:
        logger.error(f"Error updating lead {lead_id} after call: {str(e)}")
        self.retry(exc=e, countdown=TASK_DEFAULT_RETRY_DELAY * (2 ** self.request.retries))


@app.task(
    name='lead.qualify_lead',
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    queue=TASK_DEFAULT_QUEUE
)
def qualify_lead(self, lead_id: str, qualification: Union[str, int]) -> Dict[str, Any]:
    """
    Update lead qualification status as a background task.
    
    Args:
        lead_id: ID of the lead
        qualification: Qualification status (1=hot, 2=neutral, 3=cold) or string name
            
    Returns:
        Dictionary containing the updated lead details
    """
    # Convert string qualification to integer if needed
    qualification_map = {
        "hot": 1,
        "neutral": 2,
        "cold": 3
    }
    
    if isinstance(qualification, str) and qualification in qualification_map:
        qualification_value = qualification_map[qualification]
    else:
        qualification_value = int(qualification) if not isinstance(qualification, int) else qualification
    
    logger.info(f"Background task: qualifying lead {lead_id} as {qualification_value}")
    
    try:
        # Create an async event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Use a try/finally to ensure the loop gets closed
        try:
            # Get database session using context manager
            async def _qualify_lead():
                async with get_db() as session:
                    # Create service instance with proper repository
                    lead_repository = PostgresLeadRepository(session)
                    lead_service = DefaultLeadService(lead_repository)
                    
                    # Call the service method (without background task flag to avoid recursion)
                    result = await lead_service.qualify_lead(lead_id, qualification_value)
                    return result
            
            # Run the async function in the event loop
            result = loop.run_until_complete(_qualify_lead())
            logger.info(f"Successfully qualified lead: {lead_id} -> {qualification_value}")
            return result
            
        finally:
            # Clean up the event loop
            loop.close()
    
    except Exception as e:
        logger.error(f"Error qualifying lead {lead_id}: {str(e)}")
        self.retry(exc=e, countdown=TASK_DEFAULT_RETRY_DELAY * (2 ** self.request.retries))


@app.task(
    name='lead.add_tags_to_lead',
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    queue=TASK_DEFAULT_QUEUE
)
def add_tags_to_lead(self, lead_id: str, tags: List[str]) -> Dict[str, Any]:
    """
    Add tags to a lead as a background task.
    
    Args:
        lead_id: ID of the lead
        tags: List of tags to add
            
    Returns:
        Dictionary containing the updated lead details
    """
    logger.info(f"Background task: adding tags to lead {lead_id}: {tags}")
    
    try:
        # Create an async event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Use a try/finally to ensure the loop gets closed
        try:
            # Get database session using context manager
            async def _add_tags_to_lead():
                async with get_db() as session:
                    # Create service instance with proper repository
                    lead_repository = PostgresLeadRepository(session)
                    lead_service = DefaultLeadService(lead_repository)
                    
                    # Call the service method (without background task flag to avoid recursion)
                    result = await lead_service.add_tags_to_lead(lead_id, tags)
                    return result
            
            # Run the async function in the event loop
            result = loop.run_until_complete(_add_tags_to_lead())
            logger.info(f"Successfully added tags to lead: {lead_id}")
            return result
            
        finally:
            # Clean up the event loop
            loop.close()
    
    except Exception as e:
        logger.error(f"Error adding tags to lead {lead_id}: {str(e)}")
        self.retry(exc=e, countdown=TASK_DEFAULT_RETRY_DELAY * (2 ** self.request.retries))


@app.task(
    name='lead.update_lead_batch',
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    queue=TASK_DEFAULT_QUEUE
)
def update_lead_batch(self, lead_ids: List[str], update_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Update multiple leads with the same information as a background task.
    
    Args:
        lead_ids: List of lead IDs to update
        update_data: Dictionary containing update information
        
    Returns:
        Dictionary containing lists of successful and failed updates
    """
    logger.info(f"Background task: batch updating {len(lead_ids)} leads")
    
    results = {
        "successful": [],
        "failed": []
    }
    
    # Create an async event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Define async function to process all leads
        async def _update_lead_batch():
            async with get_db() as session:
                # Create repository and service
                lead_repository = PostgresLeadRepository(session)
                lead_service = DefaultLeadService(lead_repository)
                
                # Update each lead
                for lead_id in lead_ids:
                    try:
                        await lead_service.update_lead(lead_id, update_data)
                        results["successful"].append(lead_id)
                        
                    except Exception as e:
                        logger.error(f"Error updating lead {lead_id} in batch: {str(e)}")
                        results["failed"].append(lead_id)
                
                return results
        
        # Run the async function in the event loop
        batch_results = loop.run_until_complete(_update_lead_batch())
        
        logger.info(f"Batch update completed: {len(results['successful'])} successful, {len(results['failed'])} failed")
        return batch_results
        
    except Exception as e:
        logger.error(f"Error in batch update: {str(e)}")
        self.retry(exc=e, countdown=TASK_DEFAULT_RETRY_DELAY * (2 ** self.request.retries))
        
    finally:
        # Clean up the event loop
        loop.close()


# Mock repository for testing
class MockLeadRepository:
    """Mock repository for lead tasks."""
    
    def __init__(self, lead_id: Optional[str], data: Dict[str, Any]):
        """
        Initialize mock repository.
        
        Args:
            lead_id: ID of the lead to mock
            data: Data to associate with the lead
        """
        self.lead_id = lead_id
        self.data = data
    
    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """
        Mock getting a lead by ID.
        
        Args:
            lead_id: ID of the lead to get
            
        Returns:
            Lead data if found, None otherwise
        """
        if self.lead_id and self.lead_id != lead_id:
            return None
        return {"id": lead_id, **self.data}
    
    async def update_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock updating a lead.
        
        Args:
            lead_id: ID of the lead to update
            lead_data: Dictionary containing updated lead information
            
        Returns:
            Dictionary containing the updated lead details
        """
        return {"id": lead_id, **lead_data, "updated_at": datetime.now().isoformat()}
    
    async def update_lead_after_call(self, lead_id: str, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock updating a lead after a call.
        
        Args:
            lead_id: ID of the lead
            call_data: Dictionary containing call information
            
        Returns:
            Dictionary containing the updated lead details
        """
        return {"id": lead_id, "call_data": call_data, "updated_at": datetime.now().isoformat()}
    
    async def update_lead_qualification(self, lead_id: str, qualification: int) -> Dict[str, Any]:
        """
        Mock updating lead qualification.
        
        Args:
            lead_id: ID of the lead
            qualification: New qualification status
            
        Returns:
            Dictionary containing the updated lead details
        """
        return {"id": lead_id, "qualification": qualification, "updated_at": datetime.now().isoformat()}
    
    async def add_tags_to_lead(self, lead_id: str, tags: List[str]) -> Dict[str, Any]:
        """
        Mock adding tags to a lead.
        
        Args:
            lead_id: ID of the lead
            tags: List of tags to add
            
        Returns:
            Dictionary containing the updated lead details
        """
        return {"id": lead_id, "tags": tags, "updated_at": datetime.now().isoformat()} 