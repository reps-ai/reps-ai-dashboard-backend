"""
Campaign repository module.
"""
from .campaign_repository import CampaignRepository
from .implementations.postgres_campaign_repository import PostgresCampaignRepository

__all__ = ['CampaignRepository', 'PostgresCampaignRepository'] 