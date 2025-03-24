"""
Centralized error handling for the API.

This module provides standardized error handling across the application.
"""
from fastapi import HTTPException, status
from typing import Optional, Dict, Any, Type, Union
import logging

# Configure logging
logger = logging.getLogger(__name__)

class APIError(HTTPException):
    """Base class for API errors with standardized formatting."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        headers: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new API error.
        
        Args:
            status_code: HTTP status code
            detail: Human-readable error message
            error_code: Application-specific error code
            headers: Additional HTTP headers
            context: Additional context for logging
        """
        self.error_code = error_code or f"ERR_{status_code}"
        self.context = context or {}
        
        # Log the error
        log_detail = {
            "status_code": status_code,
            "error_code": self.error_code,
            "detail": detail,
            **self.context
        }
        logger.error(f"API Error: {log_detail}")
        
        super().__init__(status_code=status_code, detail=detail, headers=headers)

# Authentication and authorization errors
class AuthenticationError(APIError):
    """Error raised when authentication fails."""
    
    def __init__(
        self,
        detail: str = "Could not validate credentials",
        error_code: str = "AUTH_ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"},
            context=context
        )

class PermissionDeniedError(APIError):
    """Error raised when a user doesn't have permission for a resource."""
    
    def __init__(
        self,
        detail: str = "Not enough permissions",
        error_code: str = "PERMISSION_DENIED",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code,
            context=context
        )

# Resource errors
class ResourceNotFoundError(APIError):
    """Error raised when a requested resource is not found."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Union[str, int],
        detail: str = None,
        error_code: str = "RESOURCE_NOT_FOUND",
        context: Optional[Dict[str, Any]] = None
    ):
        if detail is None:
            detail = f"{resource_type} with ID {resource_id} not found"
            
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code,
            context={
                "resource_type": resource_type,
                "resource_id": resource_id,
                **(context or {})
            }
        )

class ResourceConflictError(APIError):
    """Error raised when there's a conflict with an existing resource."""
    
    def __init__(
        self,
        detail: str,
        error_code: str = "RESOURCE_CONFLICT",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
            context=context
        )

# Validation errors
class ValidationError(APIError):
    """Error raised when request validation fails."""
    
    def __init__(
        self,
        detail: str,
        error_code: str = "VALIDATION_ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
            context=context
        )

# External service errors
class ExternalServiceError(APIError):
    """Error raised when an external service fails."""
    
    def __init__(
        self,
        service_name: str,
        detail: str = None,
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        if detail is None:
            detail = f"Error communicating with external service: {service_name}"
            
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code=error_code,
            context={
                "service_name": service_name,
                **(context or {})
            }
        )

# Server errors
class ServerError(APIError):
    """Error raised for internal server errors."""
    
    def __init__(
        self,
        detail: str = "Internal server error",
        error_code: str = "SERVER_ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code,
            context=context
        ) 