import asyncio
import datetime
import os
import sys
from uuid import uuid4
from dotenv import load_dotenv
import re
from urllib.parse import urlparse, parse_qs

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Import the Base class
from backend.db.base import Base

# Load environment variables
load_dotenv()

# Get database connection string from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Parse the URL to remove any problematic parameters for asyncpg
parsed_url = urlparse(DATABASE_URL)
query_params = parse_qs(parsed_url.query)

# Remove sslmode parameter if present
if 'sslmode' in query_params:
    del query_params['sslmode']

# Reconstruct the URL without the sslmode parameter
clean_query = '&'.join(f"{k}={v[0]}" for k, v in query_params.items())
clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
if clean_query:
    clean_url += f"?{clean_query}"

# Convert standard PostgreSQL URL to asyncpg format
if clean_url.startswith("postgresql://"):
    DATABASE_URL = clean_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif not clean_url.startswith("postgresql+asyncpg://"):
    DATABASE_URL = f"postgresql+asyncpg://{clean_url.split('://', 1)[1]}"
else:
    DATABASE_URL = clean_url

print(f"Using database URL: {DATABASE_URL}")

# Create engine and session factory
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def seed_data():
    """
    Seed the database with mock data using direct SQL statements to avoid
    circular dependency issues with SQLAlchemy models.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Generate UUIDs for our entities
            branch_id = str(uuid4())
            user_id = str(uuid4())
            tag_vip_id = str(uuid4())
            tag_new_id = str(uuid4())
            tag_high_priority_id = str(uuid4())
            lead_john_id = str(uuid4())
            lead_jane_id = str(uuid4())
            lead_alex_id = str(uuid4())
            
            # 1. Create a branch
            await session.execute(
                text("""
                INSERT INTO branches (
                    id, name, address, phone, email, is_active, created_at, updated_at
                ) VALUES (
                    :id, :name, :address, :phone, :email, :is_active, :created_at, :updated_at
                )
                """),
                {
                    "id": branch_id,
                    "name": "Main Branch",
                    "address": "123 Fitness St, Gymville",
                    "phone": "555-123-4567",
                    "email": "main@example.com",
                    "is_active": True,
                    "created_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now()
                }
            )
            print(f"✅ Created branch with ID: {branch_id}")
            
            # 2. Create a user
            await session.execute(
                text("""
                INSERT INTO users (
                    id, username, password_hash, email, first_name, last_name, role, 
                    is_active, created_at, updated_at
                ) VALUES (
                    :id, :username, :password_hash, :email, :first_name, :last_name, :role, 
                    :is_active, :created_at, :updated_at
                )
                """),
                {
                    "id": user_id,
                    "username": "admin",
                    "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
                    "email": "admin@example.com",
                    "first_name": "Admin",
                    "last_name": "User",
                    "role": "admin",
                    "is_active": True,
                    "created_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now()
                }
            )
            print(f"✅ Created user with ID: {user_id}")
            
            # 3. Create user_branch association
            await session.execute(
                text("""
                INSERT INTO user_branch (user_id, branch_id) 
                VALUES (:user_id, :branch_id)
                """),
                {"user_id": user_id, "branch_id": branch_id}
            )
            print(f"✅ Associated user with branch")
            
            # 4. Create tags
            for tag_id, tag_name, tag_color in [
                (tag_vip_id, "VIP", "#FFD700"),
                (tag_new_id, "New", "#00FF00"),
                (tag_high_priority_id, "High Priority", "#FF0000")
            ]:
                await session.execute(
                    text("""
                    INSERT INTO tags (
                        id, name, color, created_at, updated_at
                    ) VALUES (
                        :id, :name, :color, :created_at, :updated_at
                    )
                    """),
                    {
                        "id": tag_id,
                        "name": tag_name,
                        "color": tag_color,
                        "created_at": datetime.datetime.now(),
                        "updated_at": datetime.datetime.now()
                    }
                )
            print(f"✅ Created tags")
            
            # 5. Create leads
            for lead_id, first_name, last_name, phone, email, status, source, notes, goals, assigned_to in [
                (
                    lead_john_id, "John", "Doe", "1234567890", "john.doe@example.com", 
                    "new", "Instagram Ads", "Interested in weight loss program", "Lose 20 lbs", user_id
                ),
                (
                    lead_jane_id, "Jane", "Smith", "0987654321", "jane.smith@example.com", 
                    "contacted", "Website", "Looking for personal training", "Gain muscle", user_id
                ),
                (
                    lead_alex_id, "Alex", "Johnson", "5551234567", "alex.j@example.com", 
                    "qualified", "Referral", "Recovery from knee injury", "Rehab and strengthening", None
                )
            ]:
                await session.execute(
                    text("""
                    INSERT INTO leads (
                        id, branch_id, assigned_to_user_id, first_name, last_name, phone, email,
                        lead_status, notes, fitness_goals, created_at, updated_at, source
                    ) VALUES (
                        :id, :branch_id, :assigned_to_user_id, :first_name, :last_name, :phone, :email,
                        :lead_status, :notes, :fitness_goals, :created_at, :updated_at, :source
                    )
                    """),
                    {
                        "id": lead_id,
                        "branch_id": branch_id,
                        "assigned_to_user_id": assigned_to,
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone": phone,
                        "email": email,
                        "lead_status": status,
                        "notes": notes,
                        "fitness_goals": goals,
                        "created_at": datetime.datetime.now(),
                        "updated_at": datetime.datetime.now(),
                        "source": source
                    }
                )
            print(f"✅ Created leads")
            
            # 6. Create lead-tag associations
            for lead_id, tag_id in [
                (lead_john_id, tag_vip_id),
                (lead_john_id, tag_new_id),
                (lead_jane_id, tag_new_id),
                (lead_jane_id, tag_high_priority_id),
                (lead_alex_id, tag_high_priority_id)
            ]:
                await session.execute(
                    text("""
                    INSERT INTO lead_tag (
                        lead_id, tag_id, created_at
                    ) VALUES (
                        :lead_id, :tag_id, :created_at
                    )
                    """),
                    {
                        "lead_id": lead_id,
                        "tag_id": tag_id,
                        "created_at": datetime.datetime.now()
                    }
                )
            print(f"✅ Created lead-tag associations")
            
            # 7. Create call settings for the branch
            call_settings_id = str(uuid4())
            await session.execute(
                text("""
                INSERT INTO call_settings (
                    id, branch_id, max_duration, call_hours_start, call_hours_end,
                    active_call_days, retry_attempts, retry_interval, do_not_disturb,
                    created_at, updated_at
                ) VALUES (
                    :id, :branch_id, :max_duration, :call_hours_start, :call_hours_end,
                    :active_call_days, :retry_attempts, :retry_interval, :do_not_disturb,
                    :created_at, :updated_at
                )
                """),
                {
                    "id": call_settings_id,
                    "branch_id": branch_id,
                    "max_duration": 300,  # 5 minutes
                    "call_hours_start": "09:00",
                    "call_hours_end": "17:00",
                    "active_call_days": '["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]',
                    "retry_attempts": 3,
                    "retry_interval": 24,  # hours
                    "do_not_disturb": False,
                    "created_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now()
                }
            )
            print(f"✅ Created call settings")
            
            # 8. Create AI settings for the branch
            ai_settings_id = str(uuid4())
            await session.execute(
                text("""
                INSERT INTO ai_settings (
                    id, branch_id, personality, agent_name, greeting,
                    allow_interruptions, offer_human_transfer, escalation_threshold,
                    created_at, updated_at
                ) VALUES (
                    :id, :branch_id, :personality, :agent_name, :greeting,
                    :allow_interruptions, :offer_human_transfer, :escalation_threshold,
                    :created_at, :updated_at
                )
                """),
                {
                    "id": ai_settings_id,
                    "branch_id": branch_id,
                    "personality": "friendly",
                    "agent_name": "Alex",
                    "greeting": "Hello, this is Alex from Fitness Gym. How can I help you today?",
                    "allow_interruptions": True,
                    "offer_human_transfer": True,
                    "escalation_threshold": 80,
                    "created_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now()
                }
            )
            print(f"✅ Created AI settings")
            
            # 9. Create a follow-up campaign
            campaign_id = str(uuid4())
            await session.execute(
                text("""
                INSERT INTO follow_up_campaigns (
                    id, lead_id, branch_id, name, description, start_date, end_date,
                    period, campaign_status, created_at, updated_at
                ) VALUES (
                    :id, :lead_id, :branch_id, :name, :description, :start_date, :end_date,
                    :period, :campaign_status, :created_at, :updated_at
                )
                """),
                {
                    "id": campaign_id,
                    "lead_id": lead_john_id,
                    "branch_id": branch_id,
                    "name": "Spring Membership Drive",
                    "description": "Follow-up campaign for spring membership promotion",
                    "start_date": datetime.datetime.now(),
                    "end_date": datetime.datetime.now() + datetime.timedelta(days=30),
                    "period": 7,  # days
                    "campaign_status": "active",
                    "created_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now()
                }
            )
            print(f"✅ Created follow-up campaign")
            
            # 10. Create a call log
            call_log_id = str(uuid4())
            await session.execute(
                text("""
                INSERT INTO call_logs (
                    id, lead_id, agent_user_id, duration, call_type, human_notes,
                    outcome, created_at, updated_at, call_status, start_time, end_time,
                    recording_url, transcript, summary, sentiment, campaign_id
                ) VALUES (
                    :id, :lead_id, :agent_user_id, :duration, :call_type, :human_notes,
                    :outcome, :created_at, :updated_at, :call_status, :start_time, :end_time,
                    :recording_url, :transcript, :summary, :sentiment, :campaign_id
                )
                """),
                {
                    "id": call_log_id,
                    "lead_id": lead_john_id,
                    "agent_user_id": user_id,
                    "duration": 180,  # 3 minutes
                    "call_type": "outbound",
                    "human_notes": "Lead was interested in our premium membership",
                    "outcome": "callback",
                    "created_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now(),
                    "call_status": "completed",
                    "start_time": datetime.datetime.now() - datetime.timedelta(days=1, hours=2),
                    "end_time": datetime.datetime.now() - datetime.timedelta(days=1, hours=1, minutes=57),
                    "recording_url": "https://example.com/recordings/call123.mp3",
                    "transcript": "Agent: Hi John, this is Admin from Fitness Gym. How are you today?\nJohn: I'm good, thanks for calling.",
                    "summary": "Initial contact with lead, discussed membership options",
                    "sentiment": "positive",
                    "campaign_id": campaign_id
                }
            )
            print(f"✅ Created call log")
            
            # 11. Create a follow-up call
            follow_up_call_id = str(uuid4())
            await session.execute(
                text("""
                INSERT INTO follow_up_calls (
                    id, lead_id, agent_user_id, campaign_id, number_of_calls, call_date_time,
                    duration, call_type, human_notes, outcome, call_status, recording_url,
                    transcript, summary, sentiment, created_at, updated_at
                ) VALUES (
                    :id, :lead_id, :agent_user_id, :campaign_id, :number_of_calls, :call_date_time,
                    :duration, :call_type, :human_notes, :outcome, :call_status, :recording_url,
                    :transcript, :summary, :sentiment, :created_at, :updated_at
                )
                """),
                {
                    "id": follow_up_call_id,
                    "lead_id": lead_john_id,
                    "agent_user_id": user_id,
                    "campaign_id": campaign_id,
                    "number_of_calls": 1,
                    "call_date_time": datetime.datetime.now() + datetime.timedelta(days=3),
                    "duration": None,  # Not completed yet
                    "call_type": "outbound",
                    "human_notes": None,
                    "outcome": None,
                    "call_status": "scheduled",
                    "recording_url": None,
                    "transcript": None,
                    "summary": None,
                    "sentiment": None,
                    "created_at": datetime.datetime.now(),
                    "updated_at": datetime.datetime.now()
                }
            )
            print(f"✅ Created follow-up call")
            
            # Commit the transaction
            await session.commit()
            
            print("✅ Successfully added mock data to the database")
        except Exception as e:
            await session.rollback()
            print(f"❌ Error adding mock data: {e}")
            raise

async def main():
    # Run the seeding function
    await seed_data()
    # Dispose the engine once done
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())