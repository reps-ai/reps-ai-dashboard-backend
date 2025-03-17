"""
Database helper functions for gym-related operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.gym import Gym
from ....utils.logging.logger import get_logger

logger = get_logger(__name__)

# Gym database helper functions will be implemented here 