"""
Configuration settings for the backend system.
"""
import os
from typing import Optional, Dict, Any, List

# Environment settings
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"

# Retell API settings
RETELL_API_KEY = os.getenv("RETELL_API_KEY", "")
RETELL_API_URL = os.getenv("RETELL_API_URL", "https://api.retell.io")

# Campaign settings
DEFAULT_MAX_CALLS_PER_DAY = int(os.getenv("DEFAULT_MAX_CALLS_PER_DAY", "50"))
DEFAULT_MAX_CALL_DURATION = int(os.getenv("DEFAULT_MAX_CALL_DURATION", "300"))  # in seconds
DEFAULT_RETRY_NUMBER = int(os.getenv("DEFAULT_RETRY_NUMBER", "2"))
DEFAULT_RETRY_GAP = int(os.getenv("DEFAULT_RETRY_GAP", "1"))  # in days

# Task queue settings
TASK_QUEUE_URL = os.getenv("TASK_QUEUE_URL", "redis://redis:6379/0")
TASK_QUEUE_BACKEND = os.getenv("TASK_QUEUE_BACKEND", "redis://redis:6379/0")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# AI service settings
AI_SERVICE_API_KEY = os.getenv("AI_SERVICE_API_KEY", "")
AI_SERVICE_API_URL = os.getenv("AI_SERVICE_API_URL", "")

# Call days mapping
CALL_DAYS_MAPPING = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6
}

# Lead qualification mapping
LEAD_QUALIFICATION_MAPPING = {
    "hot": 3,
    "neutral": 2,
    "cold": 1
}

# Call outcome mapping
CALL_OUTCOME_MAPPING = {
    "appointment_booked": "appointment_booked",
    "follow_up_needed": "follow_up_needed",
    "not_interested": "not_interested",
    "wrong_number": "wrong_number",
    "voicemail": "voicemail",
    "no_answer": "no_answer",
    "other": "other"
}

# Sentiment analysis mapping
SENTIMENT_MAPPING = {
    "positive": "positive",
    "neutral": "neutral",
    "negative": "negative"
} 