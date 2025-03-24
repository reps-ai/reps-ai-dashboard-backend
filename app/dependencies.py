from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Security configuration from environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

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

def verify_password(plain_password, hashed_password):
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate a password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    if not SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET_KEY environment variable not set"
        )
        
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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