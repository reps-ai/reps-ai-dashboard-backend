"""
Call task package.

This module exports background tasks for call-related operations.
"""
from .task_definitions import trigger_call_task

__all__ = [
    'trigger_call_task',
]