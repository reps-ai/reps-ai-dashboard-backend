from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, validator

class AppointmentType(str, Enum):
    CONSULTATION = "consultation"
    ASSESSMENT = "assessment"
    TRAINING = "training"
    TOUR = "tour"
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
    start_time: str = Field(
        ..., 
        description="Start time of the slot in ISO format",
        example="2025-03-25T14:00:00Z"
    )
    end_time: str = Field(
        ..., 
        description="End time of the slot in ISO format",
        example="2025-03-25T15:00:00Z"
    )
    available: bool = Field(
        ..., 
        description="Whether the time slot is available",
        example=True
    )
    
    class Config:
        schema_extra = {
            "example": {
                "start_time": "2025-03-25T14:00:00Z",
                "end_time": "2025-03-25T15:00:00Z",
                "available": True
            }
        }