"""
PostgreSQL implementation of the AnalyticsRepository interface.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc, update, delete, insert, cast, types, extract
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ...models.analytics.lead_performance import LeadPerformanceAnalytics
from ...models.analytics.call_performance import CallPerformanceAnalytics
from ...models.lead import Lead
from ...models.call.call_log import CallLog
from ...models.user import User
from ..analytics.interface import AnalyticsRepository
from ....utils.logging.logger import get_logger

logger = get_logger(__name__)

class PostgresAnalyticsRepository(AnalyticsRepository):
    """PostgreSQL implementation of the AnalyticsRepository interface."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with a database session."""
        self.session = session
    
    async def store_lead_performance_metrics(
        self,
        branch_id: str,
        metrics_data: Dict[str, Any],
        period_type: str,
        target_date: datetime
    ) -> Dict[str, Any]:
        """Store lead performance metrics for a branch."""
        try:
            # Get the gym_id from the branch_id
            branch_query = select(Lead.gym_id).where(Lead.branch_id == branch_id).limit(1)
            branch_result = await self.session.execute(branch_query)
            gym_id = branch_result.scalar_one_or_none()
            
            if not gym_id:
                logger.error(f"No gym found for branch ID: {branch_id}")
                raise ValueError(f"No gym found for branch ID: {branch_id}")
            
            # Create a new LeadPerformanceAnalytics instance
            analytics = LeadPerformanceAnalytics(
                branch_id=branch_id,
                gym_id=gym_id,
                date=target_date,
                period_type=period_type,
                total_lead_count=metrics_data.get("total_lead_count", 0),
                new_lead_count=metrics_data.get("new_lead_count", 0),
                contacted_lead_count=metrics_data.get("contacted_lead_count", 0),
                qualified_lead_count=metrics_data.get("qualified_lead_count", 0),
                converted_lead_count=metrics_data.get("converted_lead_count", 0),
                lost_lead_count=metrics_data.get("lost_lead_count", 0),
                conversion_rate=metrics_data.get("conversion_rate", 0.0),
                lead_source_distribution=metrics_data.get("lead_source_distribution", {}),
                avg_qualification_score=metrics_data.get("avg_qualification_score", None),
                growth_metrics=metrics_data.get("growth_metrics", {})
            )
            
            self.session.add(analytics)
            await self.session.commit()
            await self.session.refresh(analytics)
            
            return analytics.to_dict()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error storing lead performance metrics: {str(e)}")
            raise
    
    async def store_call_performance_metrics(
        self,
        branch_id: str,
        metrics_data: Dict[str, Any],
        period_type: str,
        target_date: datetime
    ) -> Dict[str, Any]:
        """Store call performance metrics for a branch."""
        try:
            # Get the gym_id from the branch_id
            branch_query = select(CallLog.gym_id).where(CallLog.branch_id == branch_id).limit(1)
            branch_result = await self.session.execute(branch_query)
            gym_id = branch_result.scalar_one_or_none()
            
            if not gym_id:
                logger.error(f"No gym found for branch ID: {branch_id}")
                raise ValueError(f"No gym found for branch ID: {branch_id}")
            
            # Create a new CallPerformanceAnalytics instance
            analytics = CallPerformanceAnalytics(
                branch_id=branch_id,
                gym_id=gym_id,
                date=target_date,
                period_type=period_type,
                total_call_count=metrics_data.get("total_call_count", 0),
                completed_call_count=metrics_data.get("completed_call_count", 0),
                answered_call_count=metrics_data.get("answered_call_count", 0),
                failed_call_count=metrics_data.get("failed_call_count", 0),
                outcome_distribution=metrics_data.get("outcome_distribution", {}),
                avg_call_duration=metrics_data.get("avg_call_duration", None),
                min_call_duration=metrics_data.get("min_call_duration", None),
                max_call_duration=metrics_data.get("max_call_duration", None),
                ai_call_count=metrics_data.get("ai_call_count", 0),
                human_call_count=metrics_data.get("human_call_count", 0),
                ai_success_rate=metrics_data.get("ai_success_rate", 0.0),
                human_success_rate=metrics_data.get("human_success_rate", 0.0),
                call_insights=metrics_data.get("call_insights", {}),
                pickup_rate=metrics_data.get("pickup_rate", 0.0)
            )
            
            self.session.add(analytics)
            await self.session.commit()
            await self.session.refresh(analytics)
            
            return analytics.to_dict()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error storing call performance metrics: {str(e)}")
            raise
    
    async def get_lead_performance_metrics(
        self,
        branch_id: str,
        period_type: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get lead performance metrics for a branch."""
        try:
            # Build the query
            query = (
                select(LeadPerformanceAnalytics)
                .where(
                    LeadPerformanceAnalytics.branch_id == branch_id,
                    LeadPerformanceAnalytics.period_type == period_type,
                    LeadPerformanceAnalytics.date >= start_date
                )
                .order_by(LeadPerformanceAnalytics.date.desc())
            )
            
            # Add end_date filter if provided
            if end_date:
                query = query.where(LeadPerformanceAnalytics.date <= end_date)
            
            # Execute the query
            result = await self.session.execute(query)
            metrics = result.scalars().all()
            
            # Convert to dictionaries
            return [metric.to_dict() for metric in metrics]
        except Exception as e:
            logger.error(f"Error retrieving lead performance metrics: {str(e)}")
            raise
    
    async def get_call_performance_metrics(
        self,
        branch_id: str,
        period_type: str,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get call performance metrics for a branch."""
        try:
            # Build the query
            query = (
                select(CallPerformanceAnalytics)
                .where(
                    CallPerformanceAnalytics.branch_id == branch_id,
                    CallPerformanceAnalytics.period_type == period_type,
                    CallPerformanceAnalytics.date >= start_date
                )
                .order_by(CallPerformanceAnalytics.date.desc())
            )
            
            # Add end_date filter if provided
            if end_date:
                query = query.where(CallPerformanceAnalytics.date <= end_date)
            
            # Execute the query
            result = await self.session.execute(query)
            metrics = result.scalars().all()
            
            # Convert to dictionaries
            return [metric.to_dict() for metric in metrics]
        except Exception as e:
            logger.error(f"Error retrieving call performance metrics: {str(e)}")
            raise
    
    async def get_latest_lead_performance_metrics(
        self,
        branch_id: str,
        period_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get the latest lead performance metrics for a branch."""
        try:
            # Build the query
            query = (
                select(LeadPerformanceAnalytics)
                .where(
                    LeadPerformanceAnalytics.branch_id == branch_id,
                    LeadPerformanceAnalytics.period_type == period_type
                )
                .order_by(LeadPerformanceAnalytics.date.desc())
                .limit(1)
            )
            
            # Execute the query
            result = await self.session.execute(query)
            metric = result.scalar_one_or_none()
            
            # Return the result
            return metric.to_dict() if metric else None
        except Exception as e:
            logger.error(f"Error retrieving latest lead performance metrics: {str(e)}")
            raise
    
    async def get_latest_call_performance_metrics(
        self,
        branch_id: str,
        period_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get the latest call performance metrics for a branch."""
        try:
            # Build the query
            query = (
                select(CallPerformanceAnalytics)
                .where(
                    CallPerformanceAnalytics.branch_id == branch_id,
                    CallPerformanceAnalytics.period_type == period_type
                )
                .order_by(CallPerformanceAnalytics.date.desc())
                .limit(1)
            )
            
            # Execute the query
            result = await self.session.execute(query)
            metric = result.scalar_one_or_none()
            
            # Return the result
            return metric.to_dict() if metric else None
        except Exception as e:
            logger.error(f"Error retrieving latest call performance metrics: {str(e)}")
            raise
    
    async def get_time_of_day_performance(
        self,
        branch_id: str,
        target_date: datetime
    ) -> Dict[str, Any]:
        """Get time-of-day performance metrics for a branch."""
        try:
            # Define time blocks
            time_blocks = {
                "morning": (6, 12),    # 6 AM to 12 PM
                "afternoon": (12, 17), # 12 PM to 5 PM
                "evening": (17, 22),   # 5 PM to 10 PM
                "night": (22, 6)       # 10 PM to 6 AM
            }
            
            results = {}
            
            for block_name, (start_hour, end_hour) in time_blocks.items():
                # Handle overnight blocks
                if start_hour > end_hour:
                    # For calls
                    call_query = (
                        select(func.count(CallLog.id))
                        .where(
                            CallLog.branch_id == branch_id,
                            CallLog.start_time >= target_date,
                            CallLog.start_time < target_date + timedelta(days=1),
                            or_(
                                extract('hour', CallLog.start_time) >= start_hour,
                                extract('hour', CallLog.start_time) < end_hour
                            )
                        )
                    )
                    
                    # For leads
                    lead_query = (
                        select(func.count(Lead.id))
                        .where(
                            Lead.branch_id == branch_id,
                            Lead.created_at >= target_date,
                            Lead.created_at < target_date + timedelta(days=1),
                            or_(
                                extract('hour', Lead.created_at) >= start_hour,
                                extract('hour', Lead.created_at) < end_hour
                            )
                        )
                    )
                else:
                    # For calls
                    call_query = (
                        select(func.count(CallLog.id))
                        .where(
                            CallLog.branch_id == branch_id,
                            CallLog.start_time >= target_date,
                            CallLog.start_time < target_date + timedelta(days=1),
                            extract('hour', CallLog.start_time) >= start_hour,
                            extract('hour', CallLog.start_time) < end_hour
                        )
                    )
                    
                    # For leads
                    lead_query = (
                        select(func.count(Lead.id))
                        .where(
                            Lead.branch_id == branch_id,
                            Lead.created_at >= target_date,
                            Lead.created_at < target_date + timedelta(days=1),
                            extract('hour', Lead.created_at) >= start_hour,
                            extract('hour', Lead.created_at) < end_hour
                        )
                    )
                
                # Execute queries
                call_result = await self.session.execute(call_query)
                call_count = call_result.scalar_one()
                
                lead_result = await self.session.execute(lead_query)
                lead_count = lead_result.scalar_one()
                
                # Get successful calls (appointment_booked outcome)
                if start_hour > end_hour:
                    success_query = (
                        select(func.count(CallLog.id))
                        .where(
                            CallLog.branch_id == branch_id,
                            CallLog.start_time >= target_date,
                            CallLog.start_time < target_date + timedelta(days=1),
                            or_(
                                extract('hour', CallLog.start_time) >= start_hour,
                                extract('hour', CallLog.start_time) < end_hour
                            ),
                            CallLog.outcome == "appointment_booked"
                        )
                    )
                else:
                    success_query = (
                        select(func.count(CallLog.id))
                        .where(
                            CallLog.branch_id == branch_id,
                            CallLog.start_time >= target_date,
                            CallLog.start_time < target_date + timedelta(days=1),
                            extract('hour', CallLog.start_time) >= start_hour,
                            extract('hour', CallLog.start_time) < end_hour,
                            CallLog.outcome == "appointment_booked"
                        )
                    )
                
                success_result = await self.session.execute(success_query)
                success_count = success_result.scalar_one()
                
                results[block_name] = {
                    "call_count": call_count,
                    "lead_count": lead_count,
                    "success_count": success_count,
                    "success_rate": success_count / call_count if call_count else 0
                }
            
            return results
        except Exception as e:
            logger.error(f"Error retrieving time-of-day performance: {str(e)}")
            raise
    
    async def get_customer_journey_metrics(
        self,
        branch_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get customer journey metrics for a branch."""
        try:
            # Average time from lead creation to first contact
            avg_time_to_contact_query = (
                select(func.avg(Lead.last_called - Lead.created_at))
                .where(
                    Lead.branch_id == branch_id,
                    Lead.created_at >= start_date,
                    Lead.created_at < end_date,
                    Lead.last_called.is_not(None)
                )
            )
            
            # Average time from contact to qualification
            avg_time_to_qualify_query = (
                select(func.avg(
                    # Use update_at as a proxy for qualification time
                    Lead.updated_at - Lead.last_called
                ))
                .where(
                    Lead.branch_id == branch_id,
                    Lead.created_at >= start_date,
                    Lead.created_at < end_date,
                    Lead.last_called.is_not(None),
                    Lead.lead_status == "qualified"
                )
            )
            
            # Average time from qualification to conversion
            avg_time_to_convert_query = (
                select(func.avg(
                    # Use update_at as a proxy for conversion time
                    Lead.updated_at - Lead.updated_at
                ))
                .where(
                    Lead.branch_id == branch_id,
                    Lead.created_at >= start_date,
                    Lead.created_at < end_date,
                    Lead.lead_status == "converted"
                )
            )
            
            # Execute queries
            avg_time_to_contact_result = await self.session.execute(avg_time_to_contact_query)
            avg_time_to_contact = avg_time_to_contact_result.scalar_one_or_none()
            
            avg_time_to_qualify_result = await self.session.execute(avg_time_to_qualify_query)
            avg_time_to_qualify = avg_time_to_qualify_result.scalar_one_or_none()
            
            avg_time_to_convert_result = await self.session.execute(avg_time_to_convert_query)
            avg_time_to_convert = avg_time_to_convert_result.scalar_one_or_none()
            
            # Calculate total journey time
            total_journey_time = 0
            if avg_time_to_contact:
                total_journey_time += avg_time_to_contact.total_seconds() if hasattr(avg_time_to_contact, "total_seconds") else 0
            if avg_time_to_qualify:
                total_journey_time += avg_time_to_qualify.total_seconds() if hasattr(avg_time_to_qualify, "total_seconds") else 0
            if avg_time_to_convert:
                total_journey_time += avg_time_to_convert.total_seconds() if hasattr(avg_time_to_convert, "total_seconds") else 0
            
            # Create results
            results = {
                "avg_time_to_contact_seconds": avg_time_to_contact.total_seconds() if avg_time_to_contact else None,
                "avg_time_to_qualify_seconds": avg_time_to_qualify.total_seconds() if avg_time_to_qualify else None,
                "avg_time_to_convert_seconds": avg_time_to_convert.total_seconds() if avg_time_to_convert else None,
                "total_journey_duration_seconds": total_journey_time or None
            }
            
            return results
        except Exception as e:
            logger.error(f"Error retrieving customer journey metrics: {str(e)}")
            raise
    
    async def get_staff_performance(
        self,
        branch_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Dict[str, Any]]:
        """Get staff performance metrics for a branch."""
        try:
            # Get all staff members in the branch
            staff_query = (
                select(User)
                .where(
                    User.branch_id == branch_id,
                    User.role == "staff"
                )
            )
            
            staff_result = await self.session.execute(staff_query)
            staff_members = staff_result.scalars().all()
            
            results = {}
            
            for staff in staff_members:
                # Count calls made
                calls_made_query = (
                    select(func.count(CallLog.id))
                    .where(
                        CallLog.branch_id == branch_id,
                        # Assuming staff_id is represented in the created_by field
                        # Adjust this based on your actual schema
                        CallLog.created_by == staff.id,
                        CallLog.start_time >= start_date,
                        CallLog.start_time < end_date
                    )
                )
                
                # Count successful calls
                successful_calls_query = (
                    select(func.count(CallLog.id))
                    .where(
                        CallLog.branch_id == branch_id,
                        # Adjust this based on your actual schema
                        CallLog.created_by == staff.id,
                        CallLog.start_time >= start_date,
                        CallLog.start_time < end_date,
                        CallLog.outcome == "appointment_booked"
                    )
                )
                
                # Count leads converted
                leads_converted_query = (
                    select(func.count(Lead.id))
                    .where(
                        Lead.branch_id == branch_id,
                        Lead.assigned_to_user_id == staff.id,
                        Lead.lead_status == "converted",
                        Lead.updated_at >= start_date,
                        Lead.updated_at < end_date
                    )
                )
                
                # Execute queries
                calls_made_result = await self.session.execute(calls_made_query)
                calls_made = calls_made_result.scalar_one()
                
                successful_calls_result = await self.session.execute(successful_calls_query)
                successful_calls = successful_calls_result.scalar_one()
                
                leads_converted_result = await self.session.execute(leads_converted_query)
                leads_converted = leads_converted_result.scalar_one()
                
                # Calculate metrics
                success_rate = successful_calls / calls_made if calls_made else 0
                conversion_efficiency = leads_converted / successful_calls if successful_calls else 0
                
                # Store results
                results[str(staff.id)] = {
                    "name": f"{staff.first_name} {staff.last_name}",
                    "calls_made": calls_made,
                    "successful_calls": successful_calls,
                    "success_rate": success_rate,
                    "leads_converted": leads_converted,
                    "conversion_efficiency": conversion_efficiency
                }
            
            return results
        except Exception as e:
            logger.error(f"Error retrieving staff performance: {str(e)}")
            raise
