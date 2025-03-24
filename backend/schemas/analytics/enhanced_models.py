from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from ..common.enums import LeadStatus, CallStatus, SentimentCategory

class TimeseriesMetric(BaseModel):
    timestamp: datetime
    value: float
    label: str
    category: Optional[str] = None
    metadata: Optional[Dict] = None
    model_config = ConfigDict(from_attributes=True)

class PerformanceMetrics(BaseModel):
    conversion_rate: float = Field(..., ge=0, le=1)
    response_time: float  # in minutes
    call_completion_rate: float = Field(..., ge=0, le=1)
    customer_satisfaction: float = Field(..., ge=0, le=1)
    model_config = ConfigDict(from_attributes=True)

class AgentPerformance(BaseModel):
    agent_id: str
    name: str
    metrics: PerformanceMetrics
    calls_handled: int
    leads_converted: int
    average_call_duration: float  # in minutes
    sentiment_scores: Dict[SentimentCategory, int]
    model_config = ConfigDict(from_attributes=True)

class FunnelMetrics(BaseModel):
    stage: str
    count: int
    conversion_rate: float = Field(..., ge=0, le=1)
    average_time: float  # time in stage (minutes)
    model_config = ConfigDict(from_attributes=True)

class LeadAnalytics(BaseModel):
    total_leads: int
    qualified_leads: int
    conversion_rate: float = Field(..., ge=0, le=1)
    average_qualification_score: float = Field(..., ge=0, le=1)
    leads_by_status: Dict[LeadStatus, int]
    leads_by_source: Dict[str, int]
    average_response_time: float  # in minutes
    funnel_metrics: List[FunnelMetrics]
    model_config = ConfigDict(from_attributes=True)

class CallAnalytics(BaseModel):
    total_calls: int
    completed_calls: int
    average_duration: float  # in minutes
    sentiment_distribution: Dict[SentimentCategory, int]
    completion_rate: float = Field(..., ge=0, le=1)
    calls_by_status: Dict[CallStatus, int]
    peak_hours: Dict[str, int]
    average_wait_time: float  # in minutes
    model_config = ConfigDict(from_attributes=True)

class SentimentAnalytics(BaseModel):
    overall_sentiment: float = Field(..., ge=-1, le=1)
    sentiment_trend: List[TimeseriesMetric]
    sentiment_by_category: Dict[str, float]
    key_topics: Dict[str, int]
    common_feedback: List[Dict[str, str]]
    model_config = ConfigDict(from_attributes=True)

class DashboardMetrics(BaseModel):
    period_start: datetime
    period_end: datetime
    lead_metrics: LeadAnalytics
    call_metrics: CallAnalytics
    sentiment_metrics: SentimentAnalytics
    agent_performance: List[AgentPerformance]
    trend_data: List[TimeseriesMetric]
    model_config = ConfigDict(from_attributes=True)
