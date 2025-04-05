"""
Serialization utilities for the application.
Provides serialization support for complex types like UUID and datetime.
"""

import simplejson as json
import uuid
import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

def serialize_to_json(obj: Any) -> str:
    """
    Serialize any object to JSON, properly handling UUIDs, datetimes, and other complex types.
    
    Args:
        obj: The object to serialize
        
    Returns:
        JSON string representation
    """
    return json.dumps(obj, default=_json_serializer)

def deserialize_from_json(json_str: str) -> Any:
    """
    Deserialize a JSON string to a Python object.
    
    Args:
        json_str: JSON string to deserialize
        
    Returns:
        Deserialized Python object
    """
    return json.loads(json_str)

def _json_serializer(obj: Any) -> Any:
    """
    Custom serializer for handling types that are not JSON serializable.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON-serializable representation of the object
    """
    # Handle UUID objects
    if isinstance(obj, uuid.UUID):
        return str(obj)
    
    # Handle datetime objects
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    
    # Handle time objects
    if isinstance(obj, datetime.time):
        return obj.isoformat()
    
    # Handle timedelta objects
    if isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    
    # Handle Decimal objects
    if isinstance(obj, Decimal):
        return float(obj)
    
    # Handle objects with to_dict method
    if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
        return obj.to_dict()
    
    # Handle objects with __dict__ attribute
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    
    # Raise TypeError for other non-serializable objects
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable") 