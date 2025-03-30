from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

# Import the necessary service and repository
from backend.services.call.implementation import DefaultCallService
from backend.db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository
from backend.db.connections.database import get_db

from backend.services.lead.implementation import DefaultLeadService
from backend.db.repositories.lead.implementations import PostgresLeadRepository



# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Mock User model for now
class User(BaseModel):
    id: int
    email: str
    full_name: str
    is_admin: bool = False
    gym_id: Optional[int] = None

# Mock Gym model
class Gym(BaseModel):
    id: int
    name: str
    # Add other gym fields as needed

# Mock Branch model
class Branch(BaseModel):
    id: int
    gym_id: int
    name: str
    # Add other branch fields as needed

# This is a placeholder - in a real app, get these from environment variables
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get the current authenticated user from a JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
        # In a real app, you'd fetch the user from the database
        # For now, return a mock user
        return User(
            id=user_id,
            email=payload.get("email", "user@example.com"),
            full_name=payload.get("name", "John Doe"),
            is_admin=payload.get("is_admin", False),
            gym_id=payload.get("gym_id")
        )
    except JWTError:
        raise credentials_exception

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure the user is an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_gym(current_user: User = Depends(get_current_user)) -> Gym:
    """
    Dependency to get the current gym based on the authenticated user.
    
    This ensures that users can only access data from their own gym.
    In a real application, you would fetch the gym from the database.
    """
    if current_user.gym_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any gym"
        )
    
    # In a real app, you'd fetch the gym from the database using current_user.gym_id
    # For now, return a mock gym
    return Gym(
        id=current_user.gym_id,
        name="Example Gym"
    )

async def get_current_branch(
    branch_id: int,
    current_gym: Gym = Depends(get_current_gym)
) -> Branch:
    """
    Dependency to get a specific branch within the current gym.
    
    This ensures that users can only access branches that belong to their gym.
    In a real application, you would fetch the branch from the database
    and verify it belongs to the current gym.
    """
    # In a real app, you'd fetch the branch from the database
    # and verify it belongs to current_gym.id
    
    # Mock verification - in a real app, this would be a database query
    if branch_id % 100 != current_gym.id % 100:  # Just a mock check
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found or does not belong to your gym"
        )
    
    return Branch(
        id=branch_id,
        gym_id=current_gym.id,
        name=f"Branch {branch_id}"
    )

async def get_call_service(db: AsyncSession = Depends(get_db)) -> DefaultCallService:
    """
    Dependency to get the call service instance with properly initialized repository.
    """
    call_repository = PostgresCallRepository(db)
    call_service = DefaultCallService(call_repository)

    return call_service

async def get_lead_service(db: AsyncSession = Depends(get_db)) -> DefaultLeadService:
    """
    Dependency to get the lead service instance with properly initialized repository.
    """
    lead_repository = PostgresLeadRepository(db)
    return DefaultLeadService(lead_repository)

    return call_service

