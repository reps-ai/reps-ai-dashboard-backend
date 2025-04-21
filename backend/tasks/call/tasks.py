"""
Celery tasks for call processing operations.
"""
from typing import Dict, Any, List
import asyncio
from uuid import UUID

from backend.celery_app import app
from backend.tasks.base import BaseTask
from backend.db.connections.database import get_db_session
from backend.services.call.implementation import DefaultCallService
from backend.services.lead.implementation import DefaultLeadService
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository
from backend.db.repositories.lead.implementations.postgres_lead_repository import PostgresLeadRepository


class ProcessCompletedCallTask(BaseTask):
    """Task to process a completed call and update the associated lead."""
    
    name = "backend.tasks.call.process_completed_call"
    queue = "call_tasks"
    
    def run(self, call_id: str) -> Dict[str, Any]:
        """
        Process a completed call and update the associated lead.
        
        Args:
            call_id: External ID of the completed call (from Retell)
            
        Returns:
            Dict with processing results
        """
        self.logger.info(f"Processing completed call: {call_id}")
        
        # Run the async processing in an event loop
        return asyncio.run(self._process_call(call_id))
    
    async def _process_call(self, call_id: str) -> Dict[str, Any]:
        """
        Async implementation of call processing.
        
        Args:
            call_id: External ID of the completed call
            
        Returns:
            Dict with processing results
        """
        try:
            # Get a database session
            session = await get_db_session()
            
            try:
                # Initialize repositories
                call_repo = PostgresCallRepository(session)
                lead_repo = PostgresLeadRepository(session)
                
                # Initialize services
                call_service = DefaultCallService(call_repo)
                lead_service = DefaultLeadService(lead_repo)
                
                # Get call by external ID (Retell call_id)
                call = await call_repo.get_call_by_external_id(call_id)
                
                if not call:
                    self.logger.error(f"Call with external ID {call_id} not found")
                    return {"success": False, "reason": "call_not_found"}
                
                # Extract lead ID
                lead_id = call.get("lead_id")
                
                if not lead_id:
                    self.logger.error(f"Call {call_id} has no associated lead")
                    return {"success": False, "reason": "no_lead_associated"}
                
                # Extract outcome and summary
                outcome = call.get("outcome", "unknown")
                summary = call.get("summary", "")
                
                # Log what we found
                self.logger.info(f"Call outcome: {outcome}, summary length: {len(summary)}")
                
                # Prepare data for lead update
                call_data = {
                    "outcome": outcome,
                    "notes": summary
                }
                
                # Update the lead with call information
                result = await lead_service.update_lead_after_call(str(lead_id), call_data)
                
                self.logger.info(f"Updated lead {lead_id} after call {call_id} with outcome {outcome}")
                return {
                    "success": True,
                    "call_id": call_id,
                    "lead_id": str(lead_id),
                    "outcome": outcome,
                    "processed_at": call.get("end_time", "")
                }
                
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error processing call {call_id}: {str(e)}")
                return {"success": False, "error": str(e)}
            finally:
                await session.close()
                
        except Exception as e:
            self.logger.error(f"Error obtaining database session: {str(e)}")
            return {"success": False, "error": str(e)}


# Register the task with Celery
app.register_task(ProcessCompletedCallTask())

# Create a function alias for easy importing in the webhook handler
process_completed_call = ProcessCompletedCallTask() 