"""
Lead task module.

This module exports background tasks for lead-related operations.
"""
from .task_definitions import (
    update_lead,
    update_lead_after_call,
    qualify_lead,
    add_tags_to_lead,
    update_lead_batch
)

__all__ = [
    'update_lead',
    'update_lead_after_call',
    'qualify_lead',
    'add_tags_to_lead',
    'update_lead_batch'
] 