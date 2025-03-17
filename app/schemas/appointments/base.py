from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.common.appointment_types import AppointmentType, AppointmentStatus

class AppointmentBase(BaseModel):
    lead_id: str
    type: str
    date: str
    duration: int
    status: str
    branch_id: str
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(AppointmentBase):
    pass

class AppointmentStatusUpdate(BaseModel):
    status: str 