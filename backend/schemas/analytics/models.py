from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, Field

class LeadAnalytics(BaseModel):
    total_leads: int
    qualified_leads: int
    conversion_rate: float = Field(..., ge=0, le=1)
    average_qualification_score: float = Field(..., ge=0, le=1)
    leads_by_status: Dict[str, int]
    leads_by_source: Dict[str, int]

class CallAnalytics(BaseModel):
    total_calls: int
    completed_calls: int
    average_duration: float
    sentiment_distribution: Dict[str, int]
    completion_rate: float = Field(..., ge=0, le=1)
    calls_by_status: Dict[str, int]

class TimeseriesMetric(BaseModel):
    timestamp: datetime
    value: float
    label: str

class AnalyticsResponse(BaseModel):
    lead_metrics: LeadAnalytics
    call_metrics: CallAnalytics
    trend_data: List[TimeseriesMetric]