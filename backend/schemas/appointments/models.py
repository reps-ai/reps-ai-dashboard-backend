from datetime import datetime, time
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from ..common.base import TimestampMixin
from ..common.enums import AppointmentStatus
from ..common.validators import DateTimeValidator

class TimeSlot(BaseModel):
    start_time: time
    end_time: time
    is_available: bool = True
    capacity: int = Field(default=1, ge=0)
    model_config = ConfigDict(from_attributes=True)

class DailyAvailability(BaseModel):
    date: datetime
    time_slots: List[TimeSlot]
    model_config = ConfigDict(from_attributes=True)

class AppointmentBase(BaseModel, DateTimeValidator):
    lead_id: str = Field(..., description="ID of the associated lead")
    branch_id: str = Field(..., description="ID of the branch")
    appointment_time: datetime
    duration: int = Field(..., description="Duration in minutes")
    status: AppointmentStatus = Field(default=AppointmentStatus.REQUESTED)
    service_type: str = Field(..., description="Type of service requested")
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AppointmentCreate(AppointmentBase):
    """Request model for creating new appointments"""
    pass

class AppointmentUpdate(BaseModel):
    """Request model for updating existing appointments"""
    appointment_time: Optional[datetime] = None
    duration: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AppointmentInDB(AppointmentBase, TimestampMixin):
    """Database model representation"""
    id: str
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    reminder_sent: bool = False
    last_reminder_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class AppointmentAnalytics(BaseModel):
    total_appointments: int
    completed_appointments: int
    cancellation_rate: float = Field(..., ge=0, le=1)
    no_show_rate: float = Field(..., ge=0, le=1)
    appointments_by_status: Dict[AppointmentStatus, int]
    appointments_by_service: Dict[str, int]
    average_duration: float  # in minutes
    peak_times: Dict[str, int]
    model_config = ConfigDict(from_attributes=True)
