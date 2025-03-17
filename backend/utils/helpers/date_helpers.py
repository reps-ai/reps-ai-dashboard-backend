"""
Helper functions for date operations.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional

from backend.utils.constants.enums import CallDay

def is_valid_call_day(target_date: date, call_days: List[str]) -> bool:
    """
    Check if a date is a valid call day based on the call days configuration.
    
    Args:
        target_date: Date to check
        call_days: List of call days (mon, tue, wed, etc.)
        
    Returns:
        True if the date is a valid call day, False otherwise
    """
    # Get the day of the week as an integer (0 = Monday, 6 = Sunday)
    day_of_week = target_date.weekday()
    
    # Map day of week to call day string
    day_map = {
        0: "mon",
        1: "tue",
        2: "wed",
        3: "thu",
        4: "fri",
        5: "sat",
        6: "sun"
    }
    
    return day_map[day_of_week] in call_days

def get_next_valid_call_day(start_date: date, call_days: List[str], max_days: int = 30) -> Optional[date]:
    """
    Get the next valid call day from a start date.
    
    Args:
        start_date: Start date
        call_days: List of call days (mon, tue, wed, etc.)
        max_days: Maximum number of days to check
        
    Returns:
        Next valid call day, or None if no valid day found within max_days
    """
    current_date = start_date
    
    for _ in range(max_days):
        current_date += timedelta(days=1)
        if is_valid_call_day(current_date, call_days):
            return current_date
    
    return None

def get_date_range(start_date: date, end_date: date) -> List[date]:
    """
    Get a list of dates in a range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        List of dates in the range
    """
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]

def get_valid_call_days_in_range(start_date: date, end_date: date, call_days: List[str]) -> List[date]:
    """
    Get a list of valid call days in a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        call_days: List of call days (mon, tue, wed, etc.)
        
    Returns:
        List of valid call days in the range
    """
    date_range = get_date_range(start_date, end_date)
    return [d for d in date_range if is_valid_call_day(d, call_days)] 