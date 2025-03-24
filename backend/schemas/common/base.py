from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None

class ServiceResponse(BaseModel):
    success: bool
    message: str