"""
Common database query utilities.
"""
from typing import List, Dict, Any, Optional, Type, TypeVar, Union
from sqlalchemy import select, and_, or_, func, desc, update, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from ....utils.logging.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T', bound=DeclarativeBase)

# Common database query utilities will be implemented here 