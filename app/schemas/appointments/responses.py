from pydantic import BaseModel
from typing import List, Optional
from app.schemas.appointments.base import AppointmentBase
from app.schemas.common.appointment_types import TimeSlot

class UserSummary(BaseModel):
    id: str
    first_name: str
    last_name: str

class LeadSummary(BaseModel):
    id: str
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    status: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    id: str
    branch_name: str
    created_at: str
    lead: LeadSummary

class AppointmentDetailResponse(AppointmentResponse):
    updated_at: str
    created_by: UserSummary
    reminder_sent: bool

class AppointmentStatusResponse(BaseModel):
    id: str
    status: str
    updated_at: str

class PaginationInfo(BaseModel):
    total: int
    page: int
    limit: int
    pages: int

class AppointmentListResponse(BaseModel):
    data: List[AppointmentResponse]
    pagination: PaginationInfo

class AvailabilityResponse(BaseModel):
    date: str
    available_slots: List[TimeSlot] 