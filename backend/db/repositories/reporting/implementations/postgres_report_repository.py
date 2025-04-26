"""
PostgreSQL implementation of the Report Repository interface.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
import json
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ....models.reporting.report_models import ReportTemplate, ReportDelivery, ReportSubscription
from ...reporting.interface import ReportRepository
from .....utils.logging.logger import get_logger
from .....cache.repository_cache import repository_cache

logger = get_logger(__name__)


class PostgresReportRepository(ReportRepository):
    """PostgreSQL implementation of the Report Repository interface."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with a database session."""
        self.session = session
    
    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report template."""
        try:
            template = ReportTemplate(
                name=template_data["name"],
                description=template_data.get("description"),
                template_type=template_data["template_type"],
                template_content=template_data["template_content"]
            )
            
            self.session.add(template)
            await self.session.commit()
            await self.session.refresh(template)
            
            return template.to_dict()
        except Exception as e:
            logger.error(f"Error creating report template: {str(e)}")
            await self.session.rollback()
            raise
    
    async def update_template(self, template_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing report template."""
        try:
            template_uuid = UUID(template_id)
            
            query = update(ReportTemplate).where(
                ReportTemplate.id == template_uuid
            ).values(
                **{k: v for k, v in template_data.items() if k in [
                    "name", "description", "template_type", "template_content"
                ]}
            ).returning(ReportTemplate)
            
            result = await self.session.execute(query)
            updated_template = result.scalar_one_or_none()
            
            if not updated_template:
                raise ValueError(f"Template with ID {template_id} not found")
            
            await self.session.flush()
            
            return updated_template.to_dict()
        except Exception as e:
            logger.error(f"Error updating report template: {str(e)}")
            raise
    
    @repository_cache(namespace="report_template", ttl=300)
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a report template by ID."""
        try:
            template_uuid = UUID(template_id)
            
            query = select(ReportTemplate).where(ReportTemplate.id == template_uuid)
            result = await self.session.execute(query)
            template = result.scalar_one_or_none()
            
            if not template:
                return None
            
            return template.to_dict()
        except Exception as e:
            logger.error(f"Error getting report template: {str(e)}")
            raise
    
    @repository_cache(namespace="report_templates_list", ttl=300)
    async def list_templates(self, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all report templates, optionally filtered by type."""
        try:
            query = select(ReportTemplate)
            
            if template_type:
                query = query.where(ReportTemplate.template_type == template_type)
            
            query = query.order_by(ReportTemplate.created_at.desc())
            
            result = await self.session.execute(query)
            templates = result.scalars().all()
            
            return [template.to_dict() for template in templates]
        except Exception as e:
            logger.error(f"Error listing report templates: {str(e)}")
            raise
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a report template."""
        try:
            template_uuid = UUID(template_id)
            
            # First check if there are subscriptions using this template
            subscription_query = select(ReportSubscription).where(
                ReportSubscription.template_id == template_uuid
            )
            subscription_result = await self.session.execute(subscription_query)
            subscriptions = subscription_result.scalars().all()
            
            if subscriptions:
                raise ValueError(f"Cannot delete template {template_id} because it has {len(subscriptions)} subscriptions")
            
            query = delete(ReportTemplate).where(ReportTemplate.id == template_uuid)
            result = await self.session.execute(query)
            
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting report template: {str(e)}")
            raise
    
    async def create_subscription(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report subscription."""
        try:
            # Convert string IDs to UUIDs where needed
            branch_id = UUID(subscription_data["branch_id"]) if isinstance(subscription_data["branch_id"], str) else subscription_data["branch_id"]
            gym_id = UUID(subscription_data["gym_id"]) if isinstance(subscription_data["gym_id"], str) else subscription_data["gym_id"]
            created_by = UUID(subscription_data["created_by"]) if isinstance(subscription_data["created_by"], str) else subscription_data["created_by"]
            
            template_id = None
            if subscription_data.get("template_id"):
                template_id = UUID(subscription_data["template_id"]) if isinstance(subscription_data["template_id"], str) else subscription_data["template_id"]
            
            subscription = ReportSubscription(
                branch_id=branch_id,
                gym_id=gym_id,
                report_type=subscription_data["report_type"],
                template_id=template_id,
                is_active=subscription_data.get("is_active", True),
                delivery_method=subscription_data.get("delivery_method", "email"),
                recipients=subscription_data["recipients"],
                delivery_time=subscription_data.get("delivery_time"),
                delivery_days=subscription_data.get("delivery_days"),
                created_by=created_by
            )
            
            self.session.add(subscription)
            await self.session.flush()
            await self.session.refresh(subscription)
            
            return subscription.to_dict()
        except Exception as e:
            logger.error(f"Error creating report subscription: {str(e)}")
            raise
    
    async def update_subscription(self, subscription_id: str, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing report subscription."""
        try:
            subscription_uuid = UUID(subscription_id)
            
            # Process IDs that need to be UUIDs
            if "branch_id" in subscription_data and isinstance(subscription_data["branch_id"], str):
                subscription_data["branch_id"] = UUID(subscription_data["branch_id"])
                
            if "gym_id" in subscription_data and isinstance(subscription_data["gym_id"], str):
                subscription_data["gym_id"] = UUID(subscription_data["gym_id"])
                
            if "template_id" in subscription_data and isinstance(subscription_data["template_id"], str):
                subscription_data["template_id"] = UUID(subscription_data["template_id"])
                
            if "created_by" in subscription_data and isinstance(subscription_data["created_by"], str):
                subscription_data["created_by"] = UUID(subscription_data["created_by"])
            
            query = update(ReportSubscription).where(
                ReportSubscription.id == subscription_uuid
            ).values(
                **{k: v for k, v in subscription_data.items() if k in [
                    "branch_id", "gym_id", "report_type", "template_id", "is_active",
                    "delivery_method", "recipients", "delivery_time", "delivery_days", "created_by"
                ]}
            ).returning(ReportSubscription)
            
            result = await self.session.execute(query)
            updated_subscription = result.scalar_one_or_none()
            
            if not updated_subscription:
                raise ValueError(f"Subscription with ID {subscription_id} not found")
            
            await self.session.flush()
            
            return updated_subscription.to_dict()
        except Exception as e:
            logger.error(f"Error updating report subscription: {str(e)}")
            raise
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get a report subscription by ID."""
        try:
            subscription_uuid = UUID(subscription_id)
            
            query = select(ReportSubscription).where(ReportSubscription.id == subscription_uuid)
            result = await self.session.execute(query)
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                return None
            
            return subscription.to_dict()
        except Exception as e:
            logger.error(f"Error getting report subscription: {str(e)}")
            raise
    
    async def list_subscriptions(
        self, 
        branch_id: Optional[str] = None, 
        report_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """List all report subscriptions, optionally filtered by branch, type, or status."""
        try:
            query = select(ReportSubscription)
            
            filters = []
            if branch_id:
                branch_uuid = UUID(branch_id) if isinstance(branch_id, str) else branch_id
                filters.append(ReportSubscription.branch_id == branch_uuid)
            
            if report_type:
                filters.append(ReportSubscription.report_type == report_type)
            
            if is_active is not None:
                filters.append(ReportSubscription.is_active == is_active)
            
            if filters:
                query = query.where(and_(*filters))
            
            query = query.order_by(ReportSubscription.created_at.desc())
            
            result = await self.session.execute(query)
            subscriptions = result.scalars().all()
            
            return [subscription.to_dict() for subscription in subscriptions]
        except Exception as e:
            logger.error(f"Error listing report subscriptions: {str(e)}")
            raise
    
    async def delete_subscription(self, subscription_id: str) -> bool:
        """Delete a report subscription."""
        try:
            subscription_uuid = UUID(subscription_id)
            
            query = delete(ReportSubscription).where(ReportSubscription.id == subscription_uuid)
            result = await self.session.execute(query)
            
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting report subscription: {str(e)}")
            raise
    
    async def create_delivery(self, delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report delivery record."""
        try:
            # Convert string IDs to UUIDs where needed
            branch_id = UUID(delivery_data["branch_id"]) if isinstance(delivery_data["branch_id"], str) else delivery_data["branch_id"]
            gym_id = UUID(delivery_data["gym_id"]) if isinstance(delivery_data["gym_id"], str) else delivery_data["gym_id"]
            
            template_id = None
            if delivery_data.get("template_id"):
                template_id = UUID(delivery_data["template_id"]) if isinstance(delivery_data["template_id"], str) else delivery_data["template_id"]
            
            # Convert date strings to datetime objects if needed
            report_period_start = delivery_data["report_period_start"]
            if isinstance(report_period_start, str):
                report_period_start = datetime.fromisoformat(report_period_start.replace('Z', '+00:00'))
                
            report_period_end = delivery_data["report_period_end"]
            if isinstance(report_period_end, str):
                report_period_end = datetime.fromisoformat(report_period_end.replace('Z', '+00:00'))
            
            delivery = ReportDelivery(
                report_type=delivery_data["report_type"],
                branch_id=branch_id,
                gym_id=gym_id,
                template_id=template_id,
                recipients=delivery_data["recipients"],
                report_data=delivery_data.get("report_data"),
                report_period_start=report_period_start,
                report_period_end=report_period_end,
                delivery_status=delivery_data.get("delivery_status", "pending"),
                delivery_time=delivery_data.get("delivery_time"),
                error_message=delivery_data.get("error_message")
            )
            
            self.session.add(delivery)
            await self.session.flush()
            await self.session.refresh(delivery)
            
            return delivery.to_dict()
        except Exception as e:
            logger.error(f"Error creating report delivery record: {str(e)}")
            raise
    
    async def update_delivery(self, delivery_id: str, delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing report delivery record."""
        try:
            delivery_uuid = UUID(delivery_id)
            
            # Process IDs that need to be UUIDs
            if "branch_id" in delivery_data and isinstance(delivery_data["branch_id"], str):
                delivery_data["branch_id"] = UUID(delivery_data["branch_id"])
                
            if "gym_id" in delivery_data and isinstance(delivery_data["gym_id"], str):
                delivery_data["gym_id"] = UUID(delivery_data["gym_id"])
                
            if "template_id" in delivery_data and isinstance(delivery_data["template_id"], str):
                delivery_data["template_id"] = UUID(delivery_data["template_id"])
            
            # Convert date strings to datetime objects if needed
            if "report_period_start" in delivery_data and isinstance(delivery_data["report_period_start"], str):
                delivery_data["report_period_start"] = datetime.fromisoformat(delivery_data["report_period_start"].replace('Z', '+00:00'))
                
            if "report_period_end" in delivery_data and isinstance(delivery_data["report_period_end"], str):
                delivery_data["report_period_end"] = datetime.fromisoformat(delivery_data["report_period_end"].replace('Z', '+00:00'))
                
            if "delivery_time" in delivery_data and isinstance(delivery_data["delivery_time"], str):
                delivery_data["delivery_time"] = datetime.fromisoformat(delivery_data["delivery_time"].replace('Z', '+00:00'))
            
            query = update(ReportDelivery).where(
                ReportDelivery.id == delivery_uuid
            ).values(
                **{k: v for k, v in delivery_data.items() if k in [
                    "branch_id", "gym_id", "report_type", "template_id", "recipients",
                    "report_data", "report_period_start", "report_period_end", 
                    "delivery_status", "delivery_time", "error_message"
                ]}
            ).returning(ReportDelivery)
            
            result = await self.session.execute(query)
            updated_delivery = result.scalar_one_or_none()
            
            if not updated_delivery:
                raise ValueError(f"Delivery record with ID {delivery_id} not found")
            
            await self.session.flush()
            
            return updated_delivery.to_dict()
        except Exception as e:
            logger.error(f"Error updating report delivery record: {str(e)}")
            raise
    
    async def get_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        """Get a report delivery record by ID."""
        try:
            delivery_uuid = UUID(delivery_id)
            
            query = select(ReportDelivery).where(ReportDelivery.id == delivery_uuid)
            result = await self.session.execute(query)
            delivery = result.scalar_one_or_none()
            
            if not delivery:
                return None
            
            return delivery.to_dict()
        except Exception as e:
            logger.error(f"Error getting report delivery record: {str(e)}")
            raise
    
    async def list_deliveries(
        self, 
        branch_id: Optional[str] = None,
        report_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """List all report delivery records, optionally filtered."""
        try:
            query = select(ReportDelivery)
            
            filters = []
            if branch_id:
                branch_uuid = UUID(branch_id) if isinstance(branch_id, str) else branch_id
                filters.append(ReportDelivery.branch_id == branch_uuid)
            
            if report_type:
                filters.append(ReportDelivery.report_type == report_type)
            
            if status:
                filters.append(ReportDelivery.delivery_status == status)
            
            if start_date:
                filters.append(ReportDelivery.created_at >= start_date)
            
            if end_date:
                filters.append(ReportDelivery.created_at <= end_date)
            
            if filters:
                query = query.where(and_(*filters))
            
            query = query.order_by(ReportDelivery.created_at.desc())
            
            result = await self.session.execute(query)
            deliveries = result.scalars().all()
            
            return [delivery.to_dict() for delivery in deliveries]
        except Exception as e:
            logger.error(f"Error listing report delivery records: {str(e)}")
            raise
    
    async def get_active_subscriptions_for_period(
        self,
        report_type: str,
        current_time: Optional[datetime] = None,
        day_of_week: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get active subscriptions for a specific period.
        """
        try:
            if current_time is None:
                current_time = datetime.now()
            
            current_hour_minute = current_time.strftime("%H:%M")
            
            # For weekly reports, we need to check the day of week
            query = select(ReportSubscription).where(
                ReportSubscription.is_active == True,
                ReportSubscription.report_type == report_type,
                ReportSubscription.delivery_time == current_hour_minute
            )
            
            # For weekly reports, check the day of week
            if report_type.lower() == "weekly" and day_of_week:
                query = query.where(
                    func.jsonb_contains(ReportSubscription.delivery_days, day_of_week)
                )
            
            result = await self.session.execute(query)
            subscriptions = result.scalars().all()
            
            return [subscription.to_dict() for subscription in subscriptions]
        except Exception as e:
            logger.error(f"Error getting active subscriptions: {str(e)}")
            raise

    async def get_pending_deliveries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get pending report deliveries."""
        try:
            query = select(ReportDelivery).where(
                ReportDelivery.delivery_status == "pending"
            ).order_by(
                ReportDelivery.created_at.asc()
            ).limit(limit)
            
            result = await self.session.execute(query)
            deliveries = result.scalars().all()
            
            return [delivery.to_dict() for delivery in deliveries]
        except Exception as e:
            logger.error(f"Error getting pending deliveries: {str(e)}")
            raise
