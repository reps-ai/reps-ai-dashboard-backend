from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Mock User model for now
class User(BaseModel):
    id: int
    email: str
    full_name: str
    is_admin: bool = False
    gym_id: Optional[int] = None

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