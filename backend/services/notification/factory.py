"""
Factory for creating notification service instances.
"""
from backend.services.notification.interface import NotificationService
from backend.services.notification.implementation import DefaultNotificationService


def create_notification_service() -> NotificationService:
    """
    Create a notification service instance.
    
    Returns:
        A NotificationService instance.
    """
    return DefaultNotificationService()
