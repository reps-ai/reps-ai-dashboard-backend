from enum import Enum
from pydantic import BaseModel
from typing import Optional

class AppointmentType(str, Enum):
    TOUR = "tour"
    CONSULTATION = "consultation"
    TRAINING = "training"
    FOLLOW_UP = "follow_up"
    OTHER = "other"

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELED = "canceled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

class TimeSlot(BaseModel):
    start_time: str
    end_time: str 