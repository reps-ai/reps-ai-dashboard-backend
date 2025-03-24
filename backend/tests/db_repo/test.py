import asyncio
from ...db.repositories.lead.implementations.postgres_lead_repository import PostgresLeadRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
import os

# Import base class
from ...db.base import Base

# Import all models to ensure SQLAlchemy knows about them
# Core models
from ...db.models.lead.lead import Lead
from ...db.models.gym.branch import Branch
from ...db.models.gym.gym import Gym
from ...db.models.user import User
from ...db.models.member import Member
from ...db.models.appointment import Appointment

# Call-related models
from ...db.models.call.call_log import CallLog
from ...db.models.call.follow_up_call import FollowUpCall
from ...db.models.call.call_settings import CallSettings
from ...db.models.campaign.follow_up_campaign import FollowUpCampaign

# Settings models
from ...db.models.gym.gym_settings import GymSettings
from ...db.models.voice_settings import VoiceSettings
from ...db.models.ai_settings import AISettings

# Other models
from ...db.models.gym.knowledge_base import KnowledgeBase
from ...db.models.lead.tag import Tag

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    # Remove sslmode if present
    if "?sslmode=" in DATABASE_URL or "&sslmode=" in DATABASE_URL:
        import re
        DATABASE_URL = re.sub(r'[\?&]sslmode=[^&]*', '', DATABASE_URL)
    # Convert to asyncpg format
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


async def test_get_lead_by_id():
    # Create engine with SSL config for Neon
    engine = create_async_engine(
        DATABASE_URL, 
        echo=True,
        connect_args={"ssl": True}  # This is the correct way to enable SSL for asyncpg
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        repo = PostgresLeadRepository(session)
        lead = await repo.get_lead_by_id(lead_id="11e92273-6d99-473f-9ef3-9806da9590ac")
        print(lead)


async def test_get_all_leads():
    engine = create_async_engine(
        DATABASE_URL, 
        echo=True,
        connect_args={"ssl": True}  # This is the correct way to enable SSL for asyncpg
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        repo = PostgresLeadRepository(session)
        leads = await repo.get_leads_by_gym(branch_id="84633c66-c08e-49b3-a0fd-e95c9f29997a")
        print(leads)

asyncio.run(test_get_all_leads())