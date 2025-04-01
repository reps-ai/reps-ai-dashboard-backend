from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

# Import the necessary service and repository
from backend.services.call.implementation import DefaultCallService
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository
from backend.db.connections.database import get_db
from backend.services.call.factory import create_call_service

from backend.services.lead.implementation import DefaultLeadService
from backend.db.repositories.lead.implementations import PostgresLeadRepository

# OAuth2 setup - will be used by oauth2.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

# User model expanded to include branch_id
class User(BaseModel):
    id: int
    email: str
    first_name: str  # Changed from full_name
    last_name: str   # Added for completeness
    role: str        # Added role instead of is_admin
    is_admin: bool = False  # Computed property - kept for compatibility
    gym_id: Optional[uuid.UUID] = None
    branch_id: Optional[uuid.UUID] = None

    @property
    def full_name(self) -> str:  # Add property for backward compatibility
        return f"{self.first_name} {self.last_name}"

# Mock Gym model
class Gym(BaseModel):
    id: uuid.UUID
    name: str
    # Add other gym fields as needed

# Mock Branch model
class Branch(BaseModel):
    id: uuid.UUID
    gym_id: uuid.UUID
    name: str
    # Add other branch fields as needed

# This is a placeholder - in a real app, get these from environment variables
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Create mock objects for testing
MOCK_USER_ID = 1
MOCK_GYM_ID = uuid.UUID("facd154c-9be8-40fb-995f-27ea665d3a8b")  # Valid gym ID
MOCK_BRANCH_ID = uuid.UUID("8d8808a4-22f8-4af3-aec4-bab5b44b1aa7")  # Valid branch ID

# NOTE: The actual authentication functions are now in app/auth/oauth2.py
# These functions remain as fallbacks for testing without authentication

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    TESTING MODE: Always returns a mock user without authentication.
    """
    # Import the real authentication at runtime to avoid circular imports
    from .auth.oauth2 import get_current_user as real_get_current_user
    
    # If a token is provided and we're not in testing mode, use the real authentication
    if token and token != "test":
        # Pass both token and db session to the real function
        return await real_get_current_user(token=token, session=db)
        
    # For testing, bypass token validation and return a mock user
    return User(
        id=MOCK_USER_ID,
        email="test@example.com",
        first_name="Test",  # Changed from full_name
        last_name="User",   # Added last_name
        role="admin",       # Added role
        is_admin=True,      # Keep is_admin for compatibility
        gym_id=MOCK_GYM_ID,
        branch_id=MOCK_BRANCH_ID
    )

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    TESTING MODE: Always returns an admin user.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )
    return current_user

async def get_current_gym(current_user: User = Depends(get_current_user)) -> Gym:
    """
    TESTING MODE: Always returns a mock gym without checking user association.
    
    In testing mode, this will accept any gym ID to allow accessing data across gyms.
    """
    # For testing, return a mock gym without verification
    return Gym(
        id=current_user.gym_id or MOCK_GYM_ID,
        name="Test Gym"
    )

async def get_current_branch(
    branch_id: Optional[Union[uuid.UUID, int, str]] = None,
    current_user: User = Depends(get_current_user)
) -> Branch:
    """
    TESTING MODE: Always returns a mock branch without verifying ownership.
    """
    # Use branch_id from request parameter or from current user if not specified
    branch_uuid = None
    if branch_id:
        branch_uuid = branch_id if isinstance(branch_id, uuid.UUID) else uuid.UUID(str(branch_id))
    else:
        branch_uuid = current_user.branch_id or MOCK_BRANCH_ID
        
    # For testing, return a mock branch
    return Branch(
        id=branch_uuid,
        gym_id=current_user.gym_id or MOCK_GYM_ID,
        name="Test Branch"
    )

# Service dependencies remain unchanged
async def get_call_service(db: AsyncSession = Depends(get_db)) -> DefaultCallService:
    """
    Dependency to get the call service instance with properly initialized repository.
    """
    call_repository = PostgresCallRepository(db)
    return create_call_service(call_repository=call_repository)

async def get_lead_service(db: AsyncSession = Depends(get_db)) -> DefaultLeadService:
    """
    Dependency to get the lead service instance with properly initialized repository.
    """
    lead_repository = PostgresLeadRepository(db)
    return DefaultLeadService(lead_repository)

