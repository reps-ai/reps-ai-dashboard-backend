"""
Schemas for the Analytics API.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from enum import Enum

class PeriodType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class DateRangeRequest(BaseModel):
    start_date: str = Field(
        ..., 
        description="Start date in ISO format (YYYY-MM-DD)",
        examples=["2025-04-01"]
    )
    end_date: str = Field(
        ..., 
        description="End date in ISO format (YYYY-MM-DD)",
        examples=["2025-04-30"]
    )
    period_type: PeriodType = Field(
        PeriodType.DAILY, 
        description="Type of period to analyze",
        examples=["daily"]
    )
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "start_date": "2025-04-01",
            "end_date": "2025-04-30",
            "period_type": "daily"
        }
    })

class DateRangeOptionalRequest(BaseModel):
    start_date: Optional[str] = Field(
        None, 
        description="Start date in ISO format (YYYY-MM-DD), defaults to 30 days ago if not provided",
        examples=["2025-04-01"]
    )
    end_date: Optional[str] = Field(
        None, 
        description="End date in ISO format (YYYY-MM-DD), defaults to today if not provided",
        examples=["2025-04-30"]
    )
    period_type: PeriodType = Field(
        PeriodType.DAILY, 
        description="Type of period to analyze",
        examples=["daily"]
    )
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "start_date": "2025-04-01",
            "end_date": "2025-04-30",
            "period_type": "daily"
        }
    })

class LeadPerformanceResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the metrics")
    branch_id: str = Field(..., description="Branch ID")
    date: str = Field(..., description="Date for which these metrics apply")
    period_type: str = Field(..., description="Type of period (daily, weekly, monthly)")
    total_lead_count: int = Field(..., description="Total number of leads")
    new_lead_count: int = Field(..., description="Number of new leads")
    contacted_lead_count: int = Field(..., description="Number of contacted leads")
    qualified_lead_count: int = Field(..., description="Number of qualified leads")
    converted_lead_count: int = Field(..., description="Number of converted leads")
    lost_lead_count: int = Field(..., description="Number of lost leads")
    conversion_rate: float = Field(..., description="Conversion rate (0.0-1.0)")
    lead_source_distribution: Dict[str, int] = Field(..., description="Distribution of lead sources")
    avg_qualification_score: Optional[float] = Field(None, description="Average qualification score")
    growth_metrics: Dict[str, float] = Field(..., description="Growth metrics compared to previous period")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "branch_id": "456e7890-e89b-12d3-a456-426614174000",
            "date": "2025-04-01T00:00:00Z",
            "period_type": "daily",
            "total_lead_count": 150,
            "new_lead_count": 12,
            "contacted_lead_count": 85,
            "qualified_lead_count": 45,
            "converted_lead_count": 20,
            "lost_lead_count": 15,
            "conversion_rate": 0.13,
            "lead_source_distribution": {
                "website": 75,
                "referral": 35,
                "walk_in": 15,
                "social": 25
            },
            "avg_qualification_score": 0.65,
            "growth_metrics": {
                "total_lead_growth": 0.05,
                "new_lead_growth": 0.2,
                "conversion_rate_growth": 0.1
            }
        }
    })

class CallPerformanceResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the metrics")
    branch_id: str = Field(..., description="Branch ID")
    date: str = Field(..., description="Date for which these metrics apply")
    period_type: str = Field(..., description="Type of period (daily, weekly, monthly)")
    total_call_count: int = Field(..., description="Total number of calls")
    completed_call_count: int = Field(..., description="Number of completed calls")
    answered_call_count: int = Field(..., description="Number of answered calls")
    failed_call_count: int = Field(..., description="Number of failed calls")
    outcome_distribution: Dict[str, int] = Field(..., description="Distribution of call outcomes")
    avg_call_duration: Optional[float] = Field(None, description="Average call duration in seconds")
    min_call_duration: Optional[float] = Field(None, description="Minimum call duration in seconds")
    max_call_duration: Optional[float] = Field(None, description="Maximum call duration in seconds")
    ai_call_count: Optional[int] = Field(None, description="Number of AI calls")
    human_call_count: Optional[int] = Field(None, description="Number of human calls")
    ai_success_rate: Optional[float] = Field(None, description="Success rate for AI calls")
    human_success_rate: Optional[float] = Field(None, description="Success rate for human calls")
    pickup_rate: float = Field(..., description="Call pickup rate (0.0-1.0)")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "branch_id": "456e7890-e89b-12d3-a456-426614174000",
            "date": "2025-04-01T00:00:00Z",
            "period_type": "daily",
            "total_call_count": 85,
            "completed_call_count": 65,
            "answered_call_count": 55,
            "failed_call_count": 20,
            "outcome_distribution": {
                "appointment_booked": 25,
                "not_interested": 18,
                "callback_requested": 12,
                "wrong_number": 5,
                "no_answer": 10,
                "voicemail": 15
            },
            "avg_call_duration": 175.5,
            "min_call_duration": 45,
            "max_call_duration": 512,
            "ai_call_count": 40,
            "human_call_count": 45,
            "ai_success_rate": 0.35,
            "human_success_rate": 0.42,
            "pickup_rate": 0.65
        }
    })

class LeadPerformanceListResponse(BaseModel):
    metrics: List[LeadPerformanceResponse] = Field(..., description="List of lead performance metrics")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "metrics": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "branch_id": "456e7890-e89b-12d3-a456-426614174000",
                    "date": "2025-04-01T00:00:00Z",
                    "period_type": "daily",
                    "total_lead_count": 150,
                    "new_lead_count": 12,
                    "contacted_lead_count": 85,
                    "qualified_lead_count": 45,
                    "converted_lead_count": 20,
                    "lost_lead_count": 15,
                    "conversion_rate": 0.13,
                    "lead_source_distribution": {
                        "website": 75,
                        "referral": 35,
                        "walk_in": 15,
                        "social": 25
                    },
                    "avg_qualification_score": 0.65,
                    "growth_metrics": {
                        "total_lead_growth": 0.05,
                        "new_lead_growth": 0.2,
                        "conversion_rate_growth": 0.1
                    }
                }
            ]
        }
    })

class CallPerformanceListResponse(BaseModel):
    metrics: List[CallPerformanceResponse] = Field(..., description="List of call performance metrics")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "metrics": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "branch_id": "456e7890-e89b-12d3-a456-426614174000",
                    "date": "2025-04-01T00:00:00Z",
                    "period_type": "daily",
                    "total_call_count": 85,
                    "completed_call_count": 65,
                    "answered_call_count": 55,
                    "failed_call_count": 20,
                    "outcome_distribution": {
                        "appointment_booked": 25,
                        "not_interested": 18,
                        "callback_requested": 12,
                        "wrong_number": 5,
                        "no_answer": 10,
                        "voicemail": 15
                    },
                    "avg_call_duration": 175.5,
                    "min_call_duration": 45,
                    "max_call_duration": 512,
                    "ai_call_count": 40,
                    "human_call_count": 45,
                    "ai_success_rate": 0.35,
                    "human_success_rate": 0.42,
                    "pickup_rate": 0.65
                }
            ]
        }
    })

class TimeOfDayMetrics(BaseModel):
    call_count: int = Field(..., description="Number of calls")
    lead_count: int = Field(..., description="Number of leads")
    success_count: int = Field(..., description="Number of successful outcomes")
    success_rate: float = Field(..., description="Success rate (0.0-1.0)")

class TimeOfDayResponse(BaseModel):
    morning: TimeOfDayMetrics = Field(..., description="Morning metrics (6 AM to 12 PM)")
    afternoon: TimeOfDayMetrics = Field(..., description="Afternoon metrics (12 PM to 5 PM)")
    evening: TimeOfDayMetrics = Field(..., description="Evening metrics (5 PM to 10 PM)")
    night: TimeOfDayMetrics = Field(..., description="Night metrics (10 PM to 6 AM)")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "morning": {
                "call_count": 25,
                "lead_count": 8,
                "success_count": 10,
                "success_rate": 0.4
            },
            "afternoon": {
                "call_count": 35,
                "lead_count": 12,
                "success_count": 15,
                "success_rate": 0.43
            },
            "evening": {
                "call_count": 20,
                "lead_count": 5,
                "success_count": 8,
                "success_rate": 0.4
            },
            "night": {
                "call_count": 5,
                "lead_count": 1,
                "success_count": 1,
                "success_rate": 0.2
            }
        }
    })

class CustomerJourneyResponse(BaseModel):
    avg_time_to_contact_seconds: Optional[float] = Field(None, description="Average time from lead creation to first contact in seconds")
    avg_time_to_qualify_seconds: Optional[float] = Field(None, description="Average time from contact to qualification in seconds")
    avg_time_to_convert_seconds: Optional[float] = Field(None, description="Average time from qualification to conversion in seconds")
    total_journey_duration_seconds: Optional[float] = Field(None, description="Total average journey duration in seconds")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "avg_time_to_contact_seconds": 3600,
            "avg_time_to_qualify_seconds": 172800,
            "avg_time_to_convert_seconds": 345600,
            "total_journey_duration_seconds": 522000
        }
    })

class StaffPerformanceMetrics(BaseModel):
    name: str = Field(..., description="Staff member name")
    calls_made: int = Field(..., description="Number of calls made")
    successful_calls: int = Field(..., description="Number of successful calls")
    success_rate: float = Field(..., description="Call success rate (0.0-1.0)")
    leads_converted: int = Field(..., description="Number of leads converted")
    conversion_efficiency: float = Field(..., description="Conversion efficiency (0.0-1.0)")

class StaffPerformanceResponse(BaseModel):
    staff_metrics: Dict[str, StaffPerformanceMetrics] = Field(..., description="Staff performance metrics by staff ID")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "staff_metrics": {
                "123e4567-e89b-12d3-a456-426614174000": {
                    "name": "John Doe",
                    "calls_made": 45,
                    "successful_calls": 20,
                    "success_rate": 0.44,
                    "leads_converted": 15,
                    "conversion_efficiency": 0.75
                },
                "456e7890-e89b-12d3-a456-426614174000": {
                    "name": "Jane Smith",
                    "calls_made": 52,
                    "successful_calls": 25,
                    "success_rate": 0.48,
                    "leads_converted": 18,
                    "conversion_efficiency": 0.72
                }
            }
        }
    })

class DashboardResponse(BaseModel):
    summary: Dict[str, Dict[str, Any]] = Field(..., description="Summary of metrics by time period")
    time_of_day_performance: Dict[str, TimeOfDayMetrics] = Field(..., description="Performance by time of day")
    customer_journey: CustomerJourneyResponse = Field(..., description="Customer journey metrics")
    generated_at: str = Field(..., description="Timestamp when the dashboard data was generated")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "summary": {
                "daily": {
                    "leads": {
                        "total_lead_count": 150,
                        "new_lead_count": 12,
                        "conversion_rate": 0.13
                    },
                    "calls": {
                        "total_call_count": 85,
                        "completed_call_count": 65,
                        "pickup_rate": 0.65
                    }
                },
                "weekly": {
                    "leads": {
                        "total_lead_count": 950,
                        "new_lead_count": 85,
                        "conversion_rate": 0.14
                    },
                    "calls": {
                        "total_call_count": 520,
                        "completed_call_count": 410,
                        "pickup_rate": 0.67
                    }
                }
            },
            "time_of_day_performance": {
                "morning": {
                    "call_count": 25,
                    "lead_count": 8,
                    "success_count": 10,
                    "success_rate": 0.4
                },
                "afternoon": {
                    "call_count": 35,
                    "lead_count": 12,
                    "success_count": 15,
                    "success_rate": 0.43
                },
                "evening": {
                    "call_count": 20,
                    "lead_count": 5,
                    "success_count": 8,
                    "success_rate": 0.4
                },
                "night": {
                    "call_count": 5,
                    "lead_count": 1,
                    "success_count": 1,
                    "success_rate": 0.2
                }
            },
            "customer_journey": {
                "avg_time_to_contact_seconds": 3600,
                "avg_time_to_qualify_seconds": 172800,
                "avg_time_to_convert_seconds": 345600,
                "total_journey_duration_seconds": 522000
            },
            "generated_at": "2025-04-25T12:34:56Z"
        }
    })

class CallMetricsResponse(BaseModel):
    period: Dict[str, Any] = Field(..., description="Date range for the metrics")
    volumes: Dict[str, int] = Field(..., description="Call volume metrics")
    rates: Dict[str, float] = Field(..., description="Call rate metrics")
    outcomes: Dict[str, int] = Field(..., description="Call outcome distribution")
    durations: Dict[str, float] = Field(..., description="Call duration metrics")
    daily_breakdown: List[Dict[str, Any]] = Field(..., description="Daily breakdown of metrics")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "period": {
                "start_date": "2025-04-01T00:00:00Z",
                "end_date": "2025-04-30T00:00:00Z",
                "days": 30
            },
            "volumes": {
                "total_calls": 520,
                "completed_calls": 410,
                "answered_calls": 380,
                "failed_calls": 110
            },
            "rates": {
                "completion_rate": 0.79,
                "answer_rate": 0.73
            },
            "outcomes": {
                "appointment_booked": 165,
                "not_interested": 98,
                "callback_requested": 72,
                "wrong_number": 25,
                "no_answer": 50,
                "voicemail": 110
            },
            "durations": {
                "average_duration_seconds": 182.5
            },
            "daily_breakdown": [
                {
                    "date": "2025-04-01T00:00:00Z",
                    "total_call_count": 18,
                    "completed_call_count": 15,
                    "answered_call_count": 12,
                    "failed_call_count": 3
                }
            ]
        }
    })
