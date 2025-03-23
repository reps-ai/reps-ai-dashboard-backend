from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from ..common.base import TimestampMixin
from ..common.enums import NotificationType, UserRole

class NotificationSettings(BaseModel):
    enabled: bool = True
    types: List[NotificationType] = Field(default_factory=list)
    preferences: Dict[NotificationType, bool] = Field(default_factory=dict)
    quiet_hours: Optional[Dict[str, List[str]]] = None
    model_config = ConfigDict(from_attributes=True)

class AISettings(BaseModel):
    enabled: bool = True
    model_name: str = "gpt-4"
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: int = Field(default=150, ge=1)
    custom_prompts: Optional[Dict[str, str]] = None
    model_config = ConfigDict(from_attributes=True)

class VoiceSettings(BaseModel):
    voice_id: str
    speaking_rate: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=0.0, ge=-20.0, le=20.0)
    language_code: str = "en-US"
    model_config = ConfigDict(from_attributes=True)

class CallSettings(BaseModel):
    max_duration: int = Field(default=30, description="Maximum call duration in minutes")
    recording_enabled: bool = True
    transcription_enabled: bool = True
    sentiment_analysis_enabled: bool = True
    auto_follow_up: bool = False
    retry_attempts: int = Field(default=3, ge=0, le=5)
    model_config = ConfigDict(from_attributes=True)

class GymSettings(BaseModel):
    name: str
    address: str
    contact_email: str
    contact_phone: str
    business_hours: Dict[str, List[str]]
    services: List[str]
    capacity: int = Field(..., ge=1)
    model_config = ConfigDict(from_attributes=True)

class IntegrationSettings(BaseModel):
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    webhook_url: Optional[str] = None
    settings: Optional[Dict] = None
    model_config = ConfigDict(from_attributes=True)

class UserSettings(BaseModel, TimestampMixin):
    user_id: str
    role: UserRole
    notification_settings: NotificationSettings
    ai_settings: AISettings
    voice_settings: Optional[VoiceSettings] = None
    call_settings: CallSettings
    integrations: List[IntegrationSettings] = Field(default_factory=list)
    preferences: Dict = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)
