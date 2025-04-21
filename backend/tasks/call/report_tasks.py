"""
Celery tasks for generating call reports.
"""
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, timedelta

from backend.celery_app import app
from backend.tasks.base import BaseTask
from backend.db.connections.database import get_db_session
from backend.services.call.implementation import DefaultCallService
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository


class GenerateCallReportTask(BaseTask):
    """Task to generate call reports for a branch."""
    
    name = "backend.tasks.call.generate_call_report"
    
    def run(self, branch_id: str, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a call report for a branch for a specific date.
        
        Args:
            branch_id: ID of the branch
            date: Optional date in ISO format (YYYY-MM-DD). Defaults to yesterday.
            
        Returns:
            Dict with report data
        """
        # Parse date or use yesterday
        if date:
            report_date = datetime.fromisoformat(date)
        else:
            report_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            
        self.logger.info(f"Generating call report for branch {branch_id} on {report_date.date()}")
        
        # Run the async processing in an event loop
        return asyncio.run(self._generate_report(branch_id, report_date))
    
    async def _generate_report(self, branch_id: str, report_date: datetime) -> Dict[str, Any]:
        """
        Async implementation of report generation.
        
        Args:
            branch_id: ID of the branch
            report_date: Date for the report
            
        Returns:
            Dict with report data
        """
        try:
            # Calculate date range (full day)
            start_date = report_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = report_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Get a database session
            session = await get_db_session()
            
            try:
                # Initialize repository and service
                call_repo = PostgresCallRepository(session)
                call_service = DefaultCallService(call_repo)
                
                # Get calls for the date range
                calls_result = await call_service.get_calls_by_date_range(
                    branch_id=branch_id,
                    start_date=start_date,
                    end_date=end_date,
                    page=1,
                    page_size=1000  # Get a large number for the report
                )
                
                calls = calls_result.get("calls", [])
                
                # Calculate metrics
                metrics = self._calculate_metrics(calls)
                
                # Generate the report
                report = {
                    "branch_id": branch_id,
                    "date": report_date.date().isoformat(),
                    "calls_count": len(calls),
                    "metrics": metrics,
                    "generated_at": datetime.now().isoformat(),
                }
                
                # In a full implementation, you would store the report in the database
                # await report_repository.save_report(report)
                
                self.logger.info(f"Generated call report for branch {branch_id} with {len(calls)} calls")
                return report
                
            except Exception as e:
                self.logger.error(f"Error generating report for branch {branch_id}: {str(e)}")
                return {"success": False, "error": str(e)}
            finally:
                await session.close()
                
        except Exception as e:
            self.logger.error(f"Error obtaining database session: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _calculate_metrics(self, calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate metrics from call data.
        
        Args:
            calls: List of call data
            
        Returns:
            Dict with calculated metrics
        """
        if not calls:
            return {
                "total_calls": 0,
                "completed_calls": 0,
                "average_duration": 0,
                "conversion_rate": 0,
                "outcomes": {}
            }
        
        # Initialize metrics
        total_calls = len(calls)
        completed_calls = sum(1 for call in calls if call.get("call_status") == "completed")
        duration_sum = sum(call.get("duration", 0) for call in calls if call.get("duration"))
        
        # Calculate outcomes
        outcomes = {}
        for call in calls:
            outcome = call.get("outcome", "unknown")
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        # Calculate scheduled appointments
        scheduled = outcomes.get("scheduled", 0)
        
        # Calculate metrics
        average_duration = duration_sum / completed_calls if completed_calls > 0 else 0
        conversion_rate = scheduled / total_calls if total_calls > 0 else 0
        
        return {
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "average_duration": round(average_duration, 2),
            "conversion_rate": round(conversion_rate, 4),
            "outcomes": outcomes
        }


# Register the task with Celery
app.register_task(GenerateCallReportTask())

# Create a function alias for easy importing
generate_call_report = GenerateCallReportTask() 