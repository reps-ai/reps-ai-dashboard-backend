"""
Call tasks module.
"""
from .call_processing import (
    process_call_completion,
    analyze_call_transcript,
    schedule_calls_for_campaign,
    generate_call_reports
)

__all__ = [
    'process_call_completion',
    'analyze_call_transcript',
    'schedule_calls_for_campaign',
    'generate_call_reports'
] 