"""
Enum constants for the backend system.
"""
from enum import Enum

class LeadQualification(str, Enum):
    """
    Lead qualification levels.
    """
    HOT = "hot"
    NEUTRAL = "neutral"
    COLD = "cold"

class CallDay(str, Enum):
    """
    Days of the week for call scheduling.
    """
    MONDAY = "mon"
    TUESDAY = "tue"
    WEDNESDAY = "wed"
    THURSDAY = "thu"
    FRIDAY = "fri"
    SATURDAY = "sat"
    SUNDAY = "sun"

class CallStatus(str, Enum):
    """
    Call status values.
    """
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    MISSED = "missed"
    CANCELED = "canceled"

class CallOutcome(str, Enum):
    """
    Call outcome values.
    """
    APPOINTMENT_BOOKED = "appointment_booked"
    FOLLOW_UP_NEEDED = "follow_up_needed"
    NOT_INTERESTED = "not_interested"
    WRONG_NUMBER = "wrong_number"
    VOICEMAIL = "voicemail"
    NO_ANSWER = "no_answer"
    OTHER = "other"

class CallSentiment(str, Enum):
    """
    Call sentiment values.
    """
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class LeadStatus(str, Enum):
    """
    Lead status values.
    """
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost" 