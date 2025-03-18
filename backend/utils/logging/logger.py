"""
Logging utility for the backend system.
"""
import logging
import sys
from typing import Optional

from backend.config.settings import LOG_LEVEL, LOG_FORMAT

def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with the specified name and level.
    
    Args:
        name: Name of the logger
        level: Optional log level (defaults to LOG_LEVEL from settings)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = getattr(logging, (level or LOG_LEVEL).upper())
    logger.setLevel(log_level)
    
    # Create handler if not already set up
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the specified name and level.
    
    Args:
        name: Name of the logger
        level: Optional log level (defaults to LOG_LEVEL from settings)
        
    Returns:
        Configured logger
    """
    return setup_logger(name, level) 