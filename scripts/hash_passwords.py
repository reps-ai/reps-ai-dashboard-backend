"""
One-time script to hash all user passwords in the database.

Usage:
    1. Set DATABASE_URL in environment or update directly in this script
    2. Run: python hash_passwords.py
"""
import os
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from dotenv import load_dotenv

# Import User model - adjust import path if needed
from backend.db.models.user import User

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://username:password@localhost/dbname")
print(f"Connecting to database: {DATABASE_URL}")

# Configure connection
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    # Get all users and hash their passwords
    users = session.execute(select(User)).scalars().all()
    updated_count = 0
    
    print(f"Found {len(users)} users")
    
    for user in users:
        print(f"Processing user: {user.email}")
        # Skip users that might already have hashed passwords
        if len(user.password_hash) > 50:  # Use correct field name: password_hash
            print(f"  User {user.email} already has a hashed password")
            continue
            
        # Hash the password
        hashed_password = pwd_context.hash(user.password_hash)  # Use correct field name
        
        # Update the user
        session.execute(
            update(User).where(User.id == user.id).values(password_hash=hashed_password)  # Use correct field name
        )
        updated_count += 1
    
    session.commit()
    print(f"Successfully updated passwords for {updated_count} users")
    
except Exception as e:
    session.rollback()
    print(f"Error: {str(e)}")
    
finally:
    session.close()
