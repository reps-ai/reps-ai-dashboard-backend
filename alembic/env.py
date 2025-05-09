from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine.url import make_url
from backend.db.config import settings
from backend.db.base import Base

from alembic import context
import re
from urllib.parse import urlparse, parse_qs

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Parse the DATABASE_URL to handle SSL correctly for Alembic (which needs a synchronous connection)
db_url = settings.DATABASE_URL

# 1. Convert from asyncpg to psycopg2 if needed
if '+asyncpg' in db_url:
    db_url = db_url.replace('+asyncpg', '')

# 2. Handle SSL parameters
parsed_url = urlparse(db_url)
query_params = parse_qs(parsed_url.query)

# Create a clean URL without SSL parameters
clean_url_parts = list(parsed_url)
clean_url_parts[4] = '&'.join([
    f"{k}={v[0]}" for k, v in query_params.items() 
    if k not in ['sslmode', 'ssl']
])

# Build the clean URL
clean_url = parsed_url._replace(query=clean_url_parts[4]).geturl()
if clean_url.endswith('?'):
    clean_url = clean_url[:-1]  # Remove trailing ? if there are no query params left

config.set_main_option("sqlalchemy.url", clean_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from backend.db.base import Base

# Import your models so that they are registered in Base.metadata
from backend.db.models.call.call_log import CallLog
from backend.db.models.call.call_settings import CallSettings
from backend.db.models.call.follow_up_call import FollowUpCall
from backend.db.models.lead.lead import Lead
from backend.db.models.lead.lead_tag import lead_tag
from backend.db.models.lead.tag import Tag
from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign
from backend.db.models.gym.branch import Branch
from backend.db.models.gym.gym_settings import GymSettings
from backend.db.models.gym.gym import Gym
from backend.db.models.gym.knowledge_base import KnowledgeBase
from backend.db.models.user import User
from backend.db.models.ai_settings import AISettings
from backend.db.models.appointment import Appointment
from backend.db.models.member import Member
from backend.db.models.voice_settings import VoiceSettings

# Add any other model imports you have

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    # Convert to a URL object and remove the async driver indicator
    sync_url = make_url(url).set(drivername="postgresql")
    config.set_main_option("sqlalchemy.url", str(sync_url))

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection with the context.
    """
    # Create a synchronous engine with appropriate settings
    # Get the base configuration but possibly override with SSL settings
    section = config.get_section(config.config_ini_section, {})
    
    # Check if we're connecting to Neon or another service requiring SSL
    alembic_url = config.get_main_option("sqlalchemy.url")
    connect_args = {}
    if 'neon.tech' in alembic_url:
        # For psycopg2, use sslmode instead of ssl
        connect_args['sslmode'] = 'require'
    
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
