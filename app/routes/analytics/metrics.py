"""
API endpoints for analytics data.
"""
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
import logging
import uuid

from app.dependencies import get_current_branch, Branch, get_analytics_service
from app.schemas.analytics.schemas import (
    DateRangeRequest, DateRangeOptionalRequest, 
    LeadPerformanceListResponse, CallPerformanceListResponse,
    TimeOfDayResponse, CustomerJourneyResponse, StaffPerformanceResponse,
    DashboardResponse, CallMetricsResponse
)
from backend.services.analytics.implementation import DefaultAnalyticsService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_branch: Branch = Depends(get_current_branch),
    analytics_service: DefaultAnalyticsService = Depends(get_analytics_service)
):
    """
    Get dashboard analytics data including summary metrics, time-of-day performance,
    and customer journey metrics.
    """
    try:
        logger.info(f"Generating dashboard data for branch {current_branch.id}")
        dashboard_data = await analytics_service.generate_dashboard_data(
            branch_id=str(current_branch.id)
        )
        return dashboard_data
    except Exception as e:
        logger.exception(f"Error generating dashboard data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard data: {str(e)}"
        )

@router.get("/leads/performance", response_model=LeadPerformanceListResponse)
async def get_lead_performance(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    period_type: str = Query("daily", description="Period type (daily, weekly, monthly)"),
    current_branch: Branch = Depends(get_current_branch),
    analytics_service: DefaultAnalyticsService = Depends(get_analytics_service)
):
    """
    Get lead performance metrics for a date range.
    """
    try:
        # Parse dates
        try:
            start_datetime = datetime.fromisoformat(start_date)
            end_datetime = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format (YYYY-MM-DD)."
            )
        
        # Validate period type
        if period_type not in ["daily", "weekly", "monthly"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period type. Must be one of: daily, weekly, monthly."
            )
        
        # Get metrics
        metrics = await analytics_service.analytics_repository.get_lead_performance_metrics(
            branch_id=str(current_branch.id),
            period_type=period_type,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        return {"metrics": metrics}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving lead performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve lead performance metrics: {str(e)}"
        )

@router.get("/calls/performance", response_model=CallPerformanceListResponse)
async def get_call_performance(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    period_type: str = Query("daily", description="Period type (daily, weekly, monthly)"),
    current_branch: Branch = Depends(get_current_branch),
    analytics_service: DefaultAnalyticsService = Depends(get_analytics_service)
):
    """
    Get call performance metrics for a date range.
    """
    try:
        # Parse dates
        try:
            start_datetime = datetime.fromisoformat(start_date)
            end_datetime = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format (YYYY-MM-DD)."
            )
        
        # Validate period type
        if period_type not in ["daily", "weekly", "monthly"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period type. Must be one of: daily, weekly, monthly."
            )
        
        # Get metrics
        metrics = await analytics_service.analytics_repository.get_call_performance_metrics(
            branch_id=str(current_branch.id),
            period_type=period_type,
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        return {"metrics": metrics}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving call performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve call performance metrics: {str(e)}"
        )

@router.get("/calls/metrics", response_model=CallMetricsResponse)
async def get_call_metrics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_branch: Branch = Depends(get_current_branch),
    analytics_service: DefaultAnalyticsService = Depends(get_analytics_service)
):
    """
    Get detailed call metrics including volumes, rates, and outcomes.
    """
    try:
        # Set default dates if not provided
        if not start_date:
            start_datetime = datetime.now() - timedelta(days=30)
        else:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start date format. Use ISO format (YYYY-MM-DD)."
                )
        
        if not end_date:
            end_datetime = datetime.now()
        else:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end date format. Use ISO format (YYYY-MM-DD)."
                )
        
        # Get metrics
        metrics = await analytics_service.get_call_metrics_by_date_range(
            branch_id=str(current_branch.id),
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving call metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve call metrics: {str(e)}"
        )

@router.get("/time-of-day", response_model=TimeOfDayResponse)
async def get_time_of_day_performance(
    date: Optional[str] = Query(None, description="Target date (YYYY-MM-DD), defaults to today"),
    current_branch: Branch = Depends(get_current_branch),
    analytics_service: DefaultAnalyticsService = Depends(get_analytics_service)
):
    """
    Get performance metrics broken down by time of day.
    """
    try:
        # Parse date
        if not date:
            target_date = datetime.now()
        else:
            try:
                target_date = datetime.fromisoformat(date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use ISO format (YYYY-MM-DD)."
                )
        
        # Get metrics
        metrics = await analytics_service.analytics_repository.get_time_of_day_performance(
            branch_id=str(current_branch.id),
            target_date=target_date
        )
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving time-of-day performance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve time-of-day performance: {str(e)}"
        )

@router.get("/customer-journey", response_model=CustomerJourneyResponse)
async def get_customer_journey_metrics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_branch: Branch = Depends(get_current_branch),
    analytics_service: DefaultAnalyticsService = Depends(get_analytics_service)
):
    """
    Get customer journey metrics showing average time between lead stages.
    """
    try:
        # Set default dates if not provided
        if not start_date:
            start_datetime = datetime.now() - timedelta(days=30)
        else:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start date format. Use ISO format (YYYY-MM-DD)."
                )
        
        if not end_date:
            end_datetime = datetime.now()
        else:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end date format. Use ISO format (YYYY-MM-DD)."
                )
        
        # Get metrics
        metrics = await analytics_service.analytics_repository.get_customer_journey_metrics(
            branch_id=str(current_branch.id),
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving customer journey metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve customer journey metrics: {str(e)}"
        )

@router.get("/staff-performance", response_model=StaffPerformanceResponse)
async def get_staff_performance(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_branch: Branch = Depends(get_current_branch),
    analytics_service: DefaultAnalyticsService = Depends(get_analytics_service)
):
    """
    Get performance metrics for staff members.
    """
    try:
        # Set default dates if not provided
        if not start_date:
            start_datetime = datetime.now() - timedelta(days=30)
        else:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start date format. Use ISO format (YYYY-MM-DD)."
                )
        
        if not end_date:
            end_datetime = datetime.now()
        else:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end date format. Use ISO format (YYYY-MM-DD)."
                )
        
        # Get metrics
        metrics = await analytics_service.analytics_repository.get_staff_performance(
            branch_id=str(current_branch.id),
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        return {"staff_metrics": metrics}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving staff performance metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve staff performance metrics: {str(e)}"
        )

@router.post("/generate/daily-metrics")
async def generate_daily_metrics(
    date: Optional[str] = Query(None, description="Target date (YYYY-MM-DD), defaults to yesterday"),
    current_branch: Branch = Depends(get_current_branch),
    analytics_service: DefaultAnalyticsService = Depends(get_analytics_service)
):
    """
    Manually trigger daily metrics generation for a specific date.
    """
    try:
        # Parse date
        if not date:
            target_date = datetime.now() - timedelta(days=1)
        else:
            try:
                target_date = datetime.fromisoformat(date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use ISO format (YYYY-MM-DD)."
                )
        
        # Generate metrics
        lead_metrics = await analytics_service.calculate_lead_performance_metrics(
            branch_id=str(current_branch.id),
            target_date=target_date
        )
        
        call_metrics = await analytics_service.calculate_call_performance_metrics(
            branch_id=str(current_branch.id),
            target_date=target_date
        )
        
        return {
            "message": f"Daily metrics generated for {target_date.strftime('%Y-%m-%d')}",
            "lead_metrics": lead_metrics,
            "call_metrics": call_metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating daily metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate daily metrics: {str(e)}"
        )

@router.post("/generate/weekly-metrics")
async def generate_weekly_metrics(
    date: Optional[str] = Query(None, description="Target date in the week (YYYY-MM-DD), defaults to today"),
    current_branch: Branch = Depends(get_current_branch),
    analytics_service: DefaultAnalyticsService = Depends(get_analytics_service)
):
    """
    Manually trigger weekly metrics generation for the week containing the specified date.
    """
    try:
        # Parse date
        if not date:
            target_date = datetime.now()
        else:
            try:
                target_date = datetime.fromisoformat(date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use ISO format (YYYY-MM-DD)."
                )
        
        # Generate metrics
        metrics = await analytics_service.calculate_weekly_metrics(
            branch_id=str(current_branch.id),
            target_date=target_date
        )
        
        # Get the week start date (Monday) for display purposes
        days_from_monday = target_date.weekday()
        week_start = target_date - timedelta(days=days_from_monday)
        
        return {
            "message": f"Weekly metrics generated for week starting {week_start.strftime('%Y-%m-%d')}",
            "metrics": metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating weekly metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weekly metrics: {str(e)}"
        )

@router.post("/generate/monthly-metrics")
async def generate_monthly_metrics(
    date: Optional[str] = Query(None, description="Target date in the month (YYYY-MM-DD), defaults to today"),
    current_branch: Branch = Depends(get_current_branch),
    analytics_service: DefaultAnalyticsService = Depends(get_analytics_service)
):
    """
    Manually trigger monthly metrics generation for the month containing the specified date.
    """
    try:
        # Parse date
        if not date:
            target_date = datetime.now()
        else:
            try:
                target_date = datetime.fromisoformat(date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use ISO format (YYYY-MM-DD)."
                )
        
        # Generate metrics
        metrics = await analytics_service.calculate_monthly_metrics(
            branch_id=str(current_branch.id),
            target_date=target_date
        )
        
        # Get the month name for display purposes
        month_name = target_date.strftime('%B %Y')
        
        return {
            "message": f"Monthly metrics generated for {month_name}",
            "metrics": metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating monthly metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate monthly metrics: {str(e)}"
        )
