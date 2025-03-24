import re
from typing import Optional
from datetime import datetime
from pydantic import validator

class PhoneValidator:
    @validator('phone')
    def validate_phone(cls, v: str) -> str:
        if v is None:
            return v
        cleaned = ''.join(filter(str.isdigit, v))
        if not (10 <= len(cleaned) <= 15):
            raise ValueError('Phone number must be between 10 and 15 digits')
        return v

class DateTimeValidator:
    @validator('scheduled_time', 'appointment_time', 'due_date', pre=True)
    def validate_datetime(cls, v: datetime) -> datetime:
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('Invalid datetime format')
        return v

class ScoreValidator:
    @validator('score', 'qualification_score', 'sentiment_score')
    def validate_score(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0 <= v <= 1):
            raise ValueError('Score must be between 0 and 1')
        return v

class EmailValidator:
    @validator('email')
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()
