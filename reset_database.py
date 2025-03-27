import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()  # load .env
DATABASE_URL = os.getenv("DATABASE_URL", "").replace('+asyncpg','')

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE;"))
    conn.execute(text("CREATE SCHEMA public;"))
    conn.commit()
print("Database reset complete.")
