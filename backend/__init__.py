"""This is the main module for the backend of the application."""

from .services.call.factory import create_call_service

# Don't create the service at import time, let it be created when needed
# call_service = create_call_service()
