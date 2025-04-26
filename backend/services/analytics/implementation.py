"""
Implementation of the Analytics Service.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from uuid import UUID
import json
from collections import Counter

from backend.db.repositories.analytics.interface import AnalyticsRepository
from backend.db.helpers.lead.lead_queries import get_leads_by_filters
from backend.db.helpers.call.call_queries import get_filtered_calls
from backend.services.analytics.interface import AnalyticsService
from backend.utils.logging.logger import get_logger

logger = get_logger(__name__)

class DefaultAnalyticsService(AnalyticsService):
    """Default implementation of the Analytics Service."""
    
    def __init__(self, analytics_repository: AnalyticsRepository):
        """Initialize with an analytics repository."""
        self.analytics_repository = analytics_repository
    
    async def analyze_sentiment(self, transcript: List[Dict[str, Any]]) -> str:
        """Analyze sentiment in a call transcript."""
        # Simple rule-based sentiment analysis
        # This would be replaced with a more sophisticated ML model in a production environment
        
        # Define sentiment keywords
        positive_words = [
            "happy", "great", "excellent", "good", "pleased", "satisfied", "thanks",
            "interested", "yes", "definitely", "sure", "absolutely", "perfect",
            "wonderful", "amazing", "fantastic", "excited", "love", "like"
        ]
        
        negative_words = [
            "unhappy", "bad", "poor", "terrible", "disappointed", "dissatisfied",
            "no", "not", "never", "issue", "problem", "concern", "complaint",
            "expensive", "difficult", "hard", "hate", "angry", "frustrated"
        ]
        
        # Count sentiment words
        positive_score = 0
        negative_score = 0
        
        for entry in transcript:
            text = entry.get("text", "").lower()
            
            for word in positive_words:
                positive_score += text.count(word)
                
            for word in negative_words:
                negative_score += text.count(word)
        
        # Determine overall sentiment
        if positive_score > negative_score * 1.5:  # Add a buffer for positive sentiment
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        else:
            return "neutral"
    
    async def calculate_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Calculate metrics for a campaign."""
        # This would be implemented based on your specific campaign tracking logic
        # For now, we'll return a placeholder
        return {
            "campaign_id": campaign_id,
            "total_calls": 0,
            "completed_calls": 0,
            "successful_calls": 0,
            "average_duration": 0,
            "conversion_rate": 0.0,
            "projected_roi": 0.0
        }
    
    async def generate_dashboard_data(self, branch_id: str, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate data for dashboard display."""
        # If no date is provided, use current date
        target_date = date or datetime.now()
        
        try:
            # Fetch the latest metrics
            daily_lead_metrics = await self.analytics_repository.get_latest_lead_performance_metrics(
                branch_id=branch_id,
                period_type="daily"
            )
            
            weekly_lead_metrics = await self.analytics_repository.get_latest_lead_performance_metrics(
                branch_id=branch_id,
                period_type="weekly"
            )
            
            daily_call_metrics = await self.analytics_repository.get_latest_call_performance_metrics(
                branch_id=branch_id,
                period_type="daily"
            )
            
            weekly_call_metrics = await self.analytics_repository.get_latest_call_performance_metrics(
                branch_id=branch_id,
                period_type="weekly"
            )
            
            # Get time of day performance
            time_of_day = await self.analytics_repository.get_time_of_day_performance(
                branch_id=branch_id,
                target_date=target_date
            )
            
            # Get customer journey metrics
            journey_metrics = await self.analytics_repository.get_customer_journey_metrics(
                branch_id=branch_id,
                start_date=target_date - timedelta(days=30),
                end_date=target_date
            )
            
            # Compile the dashboard data
            dashboard_data = {
                "summary": {
                    "daily": {
                        "leads": daily_lead_metrics or {},
                        "calls": daily_call_metrics or {}
                    },
                    "weekly": {
                        "leads": weekly_lead_metrics or {},
                        "calls": weekly_call_metrics or {}
                    }
                },
                "time_of_day_performance": time_of_day,
                "customer_journey": journey_metrics,
                "generated_at": datetime.now().isoformat()
            }
            
            return dashboard_data
        except Exception as e:
            logger.error(f"Error generating dashboard data: {str(e)}")
            raise
    
    async def get_call_metrics_by_date_range(
        self, 
        branch_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get call metrics for a branch within a date range."""
        try:
            # Fetch all call performance metrics in the date range
            daily_metrics = await self.analytics_repository.get_call_performance_metrics(
                branch_id=branch_id,
                period_type="daily",
                start_date=start_date,
                end_date=end_date
            )
            
            # Calculate aggregated metrics
            total_calls = sum(m.get("total_call_count", 0) for m in daily_metrics)
            completed_calls = sum(m.get("completed_call_count", 0) for m in daily_metrics)
            answered_calls = sum(m.get("answered_call_count", 0) for m in daily_metrics)
            failed_calls = sum(m.get("failed_call_count", 0) for m in daily_metrics)
            
            # Calculate rates
            completion_rate = completed_calls / total_calls if total_calls else 0
            answer_rate = answered_calls / total_calls if total_calls else 0
            
            # Aggregate outcome distribution
            all_outcomes = {}
            for m in daily_metrics:
                outcomes = m.get("outcome_distribution", {})
                for outcome, count in outcomes.items():
                    all_outcomes[outcome] = all_outcomes.get(outcome, 0) + count
            
            # Calculate average durations
            durations = [m.get("avg_call_duration") for m in daily_metrics if m.get("avg_call_duration")]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Prepare the response
            metrics = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": (end_date - start_date).days
                },
                "volumes": {
                    "total_calls": total_calls,
                    "completed_calls": completed_calls,
                    "answered_calls": answered_calls,
                    "failed_calls": failed_calls
                },
                "rates": {
                    "completion_rate": completion_rate,
                    "answer_rate": answer_rate
                },
                "outcomes": all_outcomes,
                "durations": {
                    "average_duration_seconds": avg_duration
                },
                "daily_breakdown": daily_metrics
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error retrieving call metrics: {str(e)}")
            raise
    
    async def get_lead_qualification_distribution(self, branch_id: str) -> Dict[str, int]:
        """Get distribution of lead qualifications for a branch."""
        try:
            # Fetch the latest lead performance metrics
            lead_metrics = await self.analytics_repository.get_latest_lead_performance_metrics(
                branch_id=branch_id,
                period_type="monthly"  # Using monthly for a more comprehensive view
            )
            
            if not lead_metrics:
                return {"low": 0, "medium": 0, "high": 0}
            
            # Get qualification distribution
            # This assumes your lead_metrics includes qualification_distribution
            # If not, we'd need to calculate it separately
            qualification_distribution = lead_metrics.get("qualification_distribution", {})
            
            # If no distribution is available, return defaults
            if not qualification_distribution:
                return {"low": 0, "medium": 0, "high": 0}
            
            return qualification_distribution
        except Exception as e:
            logger.error(f"Error retrieving lead qualification distribution: {str(e)}")
            raise
    
    async def get_call_outcome_distribution(
        self, 
        branch_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Get distribution of call outcomes for a branch."""
        try:
            # Set default dates if not provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Fetch call metrics for the period
            call_metrics = await self.analytics_repository.get_call_performance_metrics(
                branch_id=branch_id,
                period_type="daily",
                start_date=start_date,
                end_date=end_date
            )
            
            # Aggregate outcome distribution
            outcome_distribution = {}
            for metrics in call_metrics:
                outcomes = metrics.get("outcome_distribution", {})
                for outcome, count in outcomes.items():
                    outcome_distribution[outcome] = outcome_distribution.get(outcome, 0) + count
            
            return outcome_distribution
        except Exception as e:
            logger.error(f"Error retrieving call outcome distribution: {str(e)}")
            raise
    
    async def calculate_lead_performance_metrics(
        self, 
        branch_id: str, 
        target_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate lead performance metrics for a specific date.
        This method is typically called by a scheduled task to generate daily metrics.
        """
        try:
            # Define date ranges
            day_start = datetime(target_date.year, target_date.month, target_date.day)
            day_end = day_start + timedelta(days=1)
            
            # Get all leads for the branch
            all_leads_query = {
                "branch_id": branch_id,
                "created_at_start": None,  # No start date restriction
                "created_at_end": day_end
            }
            
            # Get leads created on the target date
            new_leads_query = {
                "branch_id": branch_id,
                "created_at_start": day_start,
                "created_at_end": day_end
            }
            
            # Get leads by status
            status_queries = {}
            for status in ["new", "contacted", "qualified", "converted", "lost"]:
                status_queries[status] = {
                    "branch_id": branch_id,
                    "status": status,
                    "created_at_end": day_end
                }
            
            # Execute queries
            all_leads = await get_leads_by_filters(branch_id, all_leads_query)
            new_leads = await get_leads_by_filters(branch_id, new_leads_query)
            status_leads = {}
            for status, query in status_queries.items():
                status_leads[status] = await get_leads_by_filters(branch_id, query)
            
            # Calculate lead counts
            total_lead_count = len(all_leads)
            new_lead_count = len(new_leads)
            
            # Calculate status distribution
            status_counts = {
                "new": len(status_leads["new"]),
                "contacted": len(status_leads["contacted"]),
                "qualified": len(status_leads["qualified"]),
                "converted": len(status_leads["converted"]),
                "lost": len(status_leads["lost"])
            }
            
            # Calculate conversion rate
            conversion_rate = status_counts["converted"] / total_lead_count if total_lead_count > 0 else 0
            
            # Calculate lead source distribution
            sources = [lead.get("source") for lead in all_leads if lead.get("source")]
            source_counts = Counter(sources)
            
            # Calculate average qualification score
            qualification_scores = [
                lead.get("qualification_score") 
                for lead in all_leads 
                if lead.get("qualification_score") is not None
            ]
            avg_qualification_score = sum(qualification_scores) / len(qualification_scores) if qualification_scores else 0
            
            # Get metrics from the previous day for growth calculation
            previous_day = day_start - timedelta(days=1)
            previous_metrics = await self.analytics_repository.get_lead_performance_metrics(
                branch_id=branch_id,
                period_type="daily",
                start_date=previous_day,
                end_date=previous_day + timedelta(days=1)
            )
            
            # Calculate growth metrics
            growth_metrics = {}
            if previous_metrics:
                prev = previous_metrics[0] if previous_metrics else {}
                growth_metrics = {
                    "total_lead_growth": (total_lead_count - prev.get("total_lead_count", 0)) / prev.get("total_lead_count", 1),
                    "new_lead_growth": (new_lead_count - prev.get("new_lead_count", 0)) / prev.get("new_lead_count", 1) if prev.get("new_lead_count", 0) > 0 else 0,
                    "conversion_rate_growth": (conversion_rate - prev.get("conversion_rate", 0)) / prev.get("conversion_rate", 1) if prev.get("conversion_rate", 0) > 0 else 0
                }
            
            # Compile metrics
            metrics = {
                "total_lead_count": total_lead_count,
                "new_lead_count": new_lead_count,
                "contacted_lead_count": status_counts["contacted"],
                "qualified_lead_count": status_counts["qualified"],
                "converted_lead_count": status_counts["converted"],
                "lost_lead_count": status_counts["lost"],
                "conversion_rate": conversion_rate,
                "lead_source_distribution": dict(source_counts),
                "avg_qualification_score": avg_qualification_score,
                "growth_metrics": growth_metrics
            }
            
            # Store metrics in the repository
            await self.analytics_repository.store_lead_performance_metrics(
                branch_id=branch_id,
                metrics_data=metrics,
                period_type="daily",
                target_date=day_start
            )
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating lead performance metrics: {str(e)}")
            raise
    
    async def calculate_call_performance_metrics(
        self, 
        branch_id: str, 
        target_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate call performance metrics for a specific date.
        This method is typically called by a scheduled task to generate daily metrics.
        """
        try:
            # Define date ranges
            day_start = datetime(target_date.year, target_date.month, target_date.day)
            day_end = day_start + timedelta(days=1)
            
            # Filter for calls on the target date
            filters = {
                "branch_id": branch_id,
                "start_date": day_start,
                "end_date": day_end
            }
            
            # Get all calls for the day
            calls = await get_filtered_calls(branch_id, filters)
            
            # Count calls by status
            total_call_count = len(calls)
            completed_calls = [call for call in calls if call.get("call_status") == "completed"]
            completed_call_count = len(completed_calls)
            
            # Count answered calls (calls that were completed and have a duration > 0)
            answered_calls = [
                call for call in completed_calls 
                if call.get("duration", 0) > 0
            ]
            answered_call_count = len(answered_calls)
            
            # Count failed calls
            failed_calls = [call for call in calls if call.get("call_status") == "failed"]
            failed_call_count = len(failed_calls)
            
            # Calculate outcome distribution
            outcomes = [call.get("outcome") for call in calls if call.get("outcome")]
            outcome_distribution = dict(Counter(outcomes))
            
            # Calculate call durations
            durations = [call.get("duration", 0) for call in completed_calls if call.get("duration") is not None]
            avg_call_duration = sum(durations) / len(durations) if durations else 0
            min_call_duration = min(durations) if durations else 0
            max_call_duration = max(durations) if durations else 0
            
            # Calculate AI vs human calls
            # Assuming a field in the call model indicating if it's an AI call
            ai_calls = [call for call in calls if call.get("is_ai_call", False)]
            human_calls = [call for call in calls if not call.get("is_ai_call", False)]
            
            ai_call_count = len(ai_calls)
            human_call_count = len(human_calls)
            
            # Calculate success rates
            ai_success = [call for call in ai_calls if call.get("outcome") == "appointment_booked"]
            human_success = [call for call in human_calls if call.get("outcome") == "appointment_booked"]
            
            ai_success_rate = len(ai_success) / ai_call_count if ai_call_count > 0 else 0
            human_success_rate = len(human_success) / human_call_count if human_call_count > 0 else 0
            
            # Calculate pickup rate
            pickup_rate = answered_call_count / total_call_count if total_call_count > 0 else 0
            
            # Compile metrics
            metrics = {
                "total_call_count": total_call_count,
                "completed_call_count": completed_call_count,
                "answered_call_count": answered_call_count,
                "failed_call_count": failed_call_count,
                "outcome_distribution": outcome_distribution,
                "avg_call_duration": avg_call_duration,
                "min_call_duration": min_call_duration,
                "max_call_duration": max_call_duration,
                "ai_call_count": ai_call_count,
                "human_call_count": human_call_count,
                "ai_success_rate": ai_success_rate,
                "human_success_rate": human_success_rate,
                "pickup_rate": pickup_rate,
                "call_insights": {}  # Would be populated with NLP-derived insights in a production system
            }
            
            # Store metrics in the repository
            await self.analytics_repository.store_call_performance_metrics(
                branch_id=branch_id,
                metrics_data=metrics,
                period_type="daily",
                target_date=day_start
            )
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating call performance metrics: {str(e)}")
            raise
    
    async def calculate_weekly_metrics(self, branch_id: str, target_date: datetime) -> Dict[str, Dict[str, Any]]:
        """Calculate weekly aggregated metrics."""
        try:
            # Get the start of the week (Monday)
            # Adjust based on your definition of the start of the week
            days_from_monday = target_date.weekday()
            week_start = target_date - timedelta(days=days_from_monday)
            week_start = datetime(week_start.year, week_start.month, week_start.day)
            week_end = week_start + timedelta(days=7)
            
            # Get daily metrics for the week
            lead_metrics = await self.analytics_repository.get_lead_performance_metrics(
                branch_id=branch_id,
                period_type="daily",
                start_date=week_start,
                end_date=week_end
            )
            
            call_metrics = await self.analytics_repository.get_call_performance_metrics(
                branch_id=branch_id,
                period_type="daily",
                start_date=week_start,
                end_date=week_end
            )
            
            # Aggregate lead metrics
            total_leads = sum(m.get("total_lead_count", 0) for m in lead_metrics)
            new_leads = sum(m.get("new_lead_count", 0) for m in lead_metrics)
            contacted_leads = sum(m.get("contacted_lead_count", 0) for m in lead_metrics)
            qualified_leads = sum(m.get("qualified_lead_count", 0) for m in lead_metrics)
            converted_leads = sum(m.get("converted_lead_count", 0) for m in lead_metrics)
            lost_leads = sum(m.get("lost_lead_count", 0) for m in lead_metrics)
            
            # Aggregate call metrics
            total_calls = sum(m.get("total_call_count", 0) for m in call_metrics)
            completed_calls = sum(m.get("completed_call_count", 0) for m in call_metrics)
            answered_calls = sum(m.get("answered_call_count", 0) for m in call_metrics)
            failed_calls = sum(m.get("failed_call_count", 0) for m in call_metrics)
            
            # Calculate rates
            lead_conversion_rate = converted_leads / total_leads if total_leads > 0 else 0
            call_completion_rate = completed_calls / total_calls if total_calls > 0 else 0
            call_answer_rate = answered_calls / total_calls if total_calls > 0 else 0
            
            # Aggregate source distribution
            source_distribution = {}
            for m in lead_metrics:
                sources = m.get("lead_source_distribution", {})
                for source, count in sources.items():
                    source_distribution[source] = source_distribution.get(source, 0) + count
            
            # Aggregate outcome distribution
            outcome_distribution = {}
            for m in call_metrics:
                outcomes = m.get("outcome_distribution", {})
                for outcome, count in outcomes.items():
                    outcome_distribution[outcome] = outcome_distribution.get(outcome, 0) + count
            
            # Calculate average durations
            durations = [m.get("avg_call_duration") for m in call_metrics if m.get("avg_call_duration")]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Get metrics from the previous week for growth calculation
            previous_week_start = week_start - timedelta(days=7)
            previous_week_lead_metrics = await self.analytics_repository.get_lead_performance_metrics(
                branch_id=branch_id,
                period_type="weekly",
                start_date=previous_week_start,
                end_date=week_start
            )
            
            previous_week_call_metrics = await self.analytics_repository.get_call_performance_metrics(
                branch_id=branch_id,
                period_type="weekly",
                start_date=previous_week_start,
                end_date=week_start
            )
            
            # Calculate growth metrics
            lead_growth = {}
            call_growth = {}
            
            if previous_week_lead_metrics:
                prev = previous_week_lead_metrics[0] if previous_week_lead_metrics else {}
                lead_growth = {
                    "total_lead_growth": (total_leads - prev.get("total_lead_count", 0)) / prev.get("total_lead_count", 1) if prev.get("total_lead_count", 0) > 0 else 0,
                    "conversion_rate_growth": (lead_conversion_rate - prev.get("conversion_rate", 0)) / prev.get("conversion_rate", 1) if prev.get("conversion_rate", 0) > 0 else 0
                }
            
            if previous_week_call_metrics:
                prev = previous_week_call_metrics[0] if previous_week_call_metrics else {}
                call_growth = {
                    "total_call_growth": (total_calls - prev.get("total_call_count", 0)) / prev.get("total_call_count", 1) if prev.get("total_call_count", 0) > 0 else 0,
                    "completion_rate_growth": (call_completion_rate - prev.get("completion_rate", 0)) / prev.get("completion_rate", 1) if prev.get("completion_rate", 0) > 0 else 0
                }
            
            # Compile weekly metrics
            weekly_lead_metrics = {
                "total_lead_count": total_leads,
                "new_lead_count": new_leads,
                "contacted_lead_count": contacted_leads,
                "qualified_lead_count": qualified_leads,
                "converted_lead_count": converted_leads,
                "lost_lead_count": lost_leads,
                "conversion_rate": lead_conversion_rate,
                "lead_source_distribution": source_distribution,
                "growth_metrics": lead_growth
            }
            
            weekly_call_metrics = {
                "total_call_count": total_calls,
                "completed_call_count": completed_calls,
                "answered_call_count": answered_calls,
                "failed_call_count": failed_calls,
                "outcome_distribution": outcome_distribution,
                "avg_call_duration": avg_duration,
                "completion_rate": call_completion_rate,
                "answer_rate": call_answer_rate,
                "growth_metrics": call_growth
            }
            
            # Store weekly metrics
            await self.analytics_repository.store_lead_performance_metrics(
                branch_id=branch_id,
                metrics_data=weekly_lead_metrics,
                period_type="weekly",
                target_date=week_start
            )
            
            await self.analytics_repository.store_call_performance_metrics(
                branch_id=branch_id,
                metrics_data=weekly_call_metrics,
                period_type="weekly",
                target_date=week_start
            )
            
            return {
                "lead_metrics": weekly_lead_metrics,
                "call_metrics": weekly_call_metrics
            }
        except Exception as e:
            logger.error(f"Error calculating weekly metrics: {str(e)}")
            raise
    
    async def calculate_monthly_metrics(self, branch_id: str, target_date: datetime) -> Dict[str, Dict[str, Any]]:
        """Calculate monthly aggregated metrics."""
        try:
            # Get the start of the month
            month_start = datetime(target_date.year, target_date.month, 1)
            # Get the start of the next month
            if target_date.month == 12:
                next_month_start = datetime(target_date.year + 1, 1, 1)
            else:
                next_month_start = datetime(target_date.year, target_date.month + 1, 1)
            
            # Get daily metrics for the month
            lead_metrics = await self.analytics_repository.get_lead_performance_metrics(
                branch_id=branch_id,
                period_type="daily",
                start_date=month_start,
                end_date=next_month_start
            )
            
            call_metrics = await self.analytics_repository.get_call_performance_metrics(
                branch_id=branch_id,
                period_type="daily",
                start_date=month_start,
                end_date=next_month_start
            )
            
            # Aggregate metrics similar to weekly metrics
            # This is similar to the weekly calculation but with different date ranges
            
            # Aggregate lead metrics
            total_leads = sum(m.get("total_lead_count", 0) for m in lead_metrics)
            new_leads = sum(m.get("new_lead_count", 0) for m in lead_metrics)
            contacted_leads = sum(m.get("contacted_lead_count", 0) for m in lead_metrics)
            qualified_leads = sum(m.get("qualified_lead_count", 0) for m in lead_metrics)
            converted_leads = sum(m.get("converted_lead_count", 0) for m in lead_metrics)
            lost_leads = sum(m.get("lost_lead_count", 0) for m in lead_metrics)
            
            # Aggregate call metrics
            total_calls = sum(m.get("total_call_count", 0) for m in call_metrics)
            completed_calls = sum(m.get("completed_call_count", 0) for m in call_metrics)
            answered_calls = sum(m.get("answered_call_count", 0) for m in call_metrics)
            failed_calls = sum(m.get("failed_call_count", 0) for m in call_metrics)
            
            # Calculate rates
            lead_conversion_rate = converted_leads / total_leads if total_leads > 0 else 0
            call_completion_rate = completed_calls / total_calls if total_calls > 0 else 0
            call_answer_rate = answered_calls / total_calls if total_calls > 0 else 0
            
            # Aggregate source distribution
            source_distribution = {}
            for m in lead_metrics:
                sources = m.get("lead_source_distribution", {})
                for source, count in sources.items():
                    source_distribution[source] = source_distribution.get(source, 0) + count
            
            # Aggregate outcome distribution
            outcome_distribution = {}
            for m in call_metrics:
                outcomes = m.get("outcome_distribution", {})
                for outcome, count in outcomes.items():
                    outcome_distribution[outcome] = outcome_distribution.get(outcome, 0) + count
            
            # Calculate average durations
            durations = [m.get("avg_call_duration") for m in call_metrics if m.get("avg_call_duration")]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Get previous month metrics
            # If current month is January, the previous month is December of the previous year
            if month_start.month == 1:
                prev_month_start = datetime(month_start.year - 1, 12, 1)
            else:
                prev_month_start = datetime(month_start.year, month_start.month - 1, 1)
                
            prev_month_end = month_start
            
            previous_month_lead_metrics = await self.analytics_repository.get_lead_performance_metrics(
                branch_id=branch_id,
                period_type="monthly",
                start_date=prev_month_start,
                end_date=prev_month_end
            )
            
            previous_month_call_metrics = await self.analytics_repository.get_call_performance_metrics(
                branch_id=branch_id,
                period_type="monthly",
                start_date=prev_month_start,
                end_date=prev_month_end
            )
            
            # Calculate growth metrics
            lead_growth = {}
            call_growth = {}
            
            if previous_month_lead_metrics:
                prev = previous_month_lead_metrics[0] if previous_month_lead_metrics else {}
                lead_growth = {
                    "total_lead_growth": (total_leads - prev.get("total_lead_count", 0)) / prev.get("total_lead_count", 1) if prev.get("total_lead_count", 0) > 0 else 0,
                    "conversion_rate_growth": (lead_conversion_rate - prev.get("conversion_rate", 0)) / prev.get("conversion_rate", 1) if prev.get("conversion_rate", 0) > 0 else 0
                }
            
            if previous_month_call_metrics:
                prev = previous_month_call_metrics[0] if previous_month_call_metrics else {}
                call_growth = {
                    "total_call_growth": (total_calls - prev.get("total_call_count", 0)) / prev.get("total_call_count", 1) if prev.get("total_call_count", 0) > 0 else 0,
                    "completion_rate_growth": (call_completion_rate - prev.get("completion_rate", 0)) / prev.get("completion_rate", 1) if prev.get("completion_rate", 0) > 0 else 0
                }
            
            # Compile monthly metrics
            monthly_lead_metrics = {
                "total_lead_count": total_leads,
                "new_lead_count": new_leads,
                "contacted_lead_count": contacted_leads,
                "qualified_lead_count": qualified_leads,
                "converted_lead_count": converted_leads,
                "lost_lead_count": lost_leads,
                "conversion_rate": lead_conversion_rate,
                "lead_source_distribution": source_distribution,
                "growth_metrics": lead_growth
            }
            
            monthly_call_metrics = {
                "total_call_count": total_calls,
                "completed_call_count": completed_calls,
                "answered_call_count": answered_calls,
                "failed_call_count": failed_calls,
                "outcome_distribution": outcome_distribution,
                "avg_call_duration": avg_duration,
                "completion_rate": call_completion_rate,
                "answer_rate": call_answer_rate,
                "growth_metrics": call_growth
            }
            
            # Store monthly metrics
            await self.analytics_repository.store_lead_performance_metrics(
                branch_id=branch_id,
                metrics_data=monthly_lead_metrics,
                period_type="monthly",
                target_date=month_start
            )
            
            await self.analytics_repository.store_call_performance_metrics(
                branch_id=branch_id,
                metrics_data=monthly_call_metrics,
                period_type="monthly",
                target_date=month_start
            )
            
            return {
                "lead_metrics": monthly_lead_metrics,
                "call_metrics": monthly_call_metrics
            }
        except Exception as e:
            logger.error(f"Error calculating monthly metrics: {str(e)}")
            raise
