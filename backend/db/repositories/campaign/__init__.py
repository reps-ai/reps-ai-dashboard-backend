"""
Campaign repository module.
"""
from .campaign_repository import CampaignRepository
from .factory import create_campaign_repository

__all__ = ['CampaignRepository', 'create_campaign_repository']