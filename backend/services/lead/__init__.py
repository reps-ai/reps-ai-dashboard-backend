"""
Lead service module.
"""
from .interface import LeadService
from .implementation import DefaultLeadService
from .factory import LeadServiceFactory

__all__ = ['LeadService', 'DefaultLeadService', 'LeadServiceFactory'] 