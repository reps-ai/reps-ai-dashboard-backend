"""
Celery tasks for lead qualification and processing.
"""
from typing import List, Optional

from backend.celery_app import app
from backend.tasks.base import BaseTask


class LeadService:
    """
    Service class for lead-related operations.
    
    This would typically interact with your database repository.
    """
    
    def qualify_lead(self, lead_id: str) -> bool:
        """
        Qualify a lead based on criteria and update status.
        
        Args:
            lead_id: Unique identifier for the lead.
            
        Returns:
            bool: True if lead was successfully qualified.
        """
        # Implement your lead qualification logic here
        # This would typically:
        # 1. Fetch lead data from database
        # 2. Apply qualification rules
        # 3. Update lead status
        # 4. Save changes
        print(f"Qualifying lead {lead_id}")
        return True
    
    def qualify_multiple_leads(self, lead_ids: List[str]) -> int:
        """
        Qualify multiple leads at once.
        
        Args:
            lead_ids: List of lead identifiers.
            
        Returns:
            int: Number of leads successfully qualified.
        """
        successful = 0
        for lead_id in lead_ids:
            if self.qualify_lead(lead_id):
                successful += 1
        return successful
    
    def get_pending_leads(self, limit: Optional[int] = 100) -> List[str]:
        """
        Get leads that need qualification.
        
        Args:
            limit: Maximum number of leads to retrieve.
            
        Returns:
            List of lead IDs that need qualification.
        """
        # This would typically query your database for leads
        # that need qualification based on some criteria
        return ["sample-lead-1", "sample-lead-2"]


class QualifyLeadTask(BaseTask):
    """Task to qualify a single lead."""
    
    name = "backend.tasks.lead.qualify_lead"
    service_class = LeadService
    
    def run(self, lead_id: str) -> bool:
        """
        Qualify a single lead.
        
        Args:
            lead_id: Unique identifier for the lead.
            
        Returns:
            bool: True if lead was successfully qualified.
        """
        self.logger.info(f"Processing lead qualification for {lead_id}")
        service = self.get_service()
        return service.qualify_lead(lead_id)


class QualifyMultipleLeadsTask(BaseTask):
    """Task to qualify multiple leads at once."""
    
    name = "backend.tasks.lead.qualify_multiple_leads"
    service_class = LeadService
    
    def run(self, lead_ids: List[str]) -> int:
        """
        Qualify multiple leads.
        
        Args:
            lead_ids: List of lead identifiers.
            
        Returns:
            int: Number of leads successfully qualified.
        """
        self.logger.info(f"Processing qualification for {len(lead_ids)} leads")
        service = self.get_service()
        return service.qualify_multiple_leads(lead_ids)


@app.task(
    name="backend.tasks.lead.tasks.qualify_pending_leads",
    base=BaseTask,
    bind=True
)
def qualify_pending_leads(self, limit: int = 100) -> int:
    """
    Find leads pending qualification and process them.
    
    Args:
        limit: Maximum number of leads to process.
        
    Returns:
        int: Number of leads processed.
    """
    self.logger.info(f"Finding and qualifying up to {limit} pending leads")
    
    # Instantiate the service
    service = LeadService()
    
    # Get leads that need qualification
    lead_ids = service.get_pending_leads(limit)
    
    if not lead_ids:
        self.logger.info("No pending leads found for qualification")
        return 0
    
    # Qualify the leads
    results = service.qualify_multiple_leads(lead_ids)
    
    self.logger.info(f"Qualified {results} leads out of {len(lead_ids)}")
    return results


# Register class-based tasks with Celery
app.register_task(QualifyLeadTask())
app.register_task(QualifyMultipleLeadsTask()) 