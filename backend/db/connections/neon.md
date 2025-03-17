# 🚀 Switching from Local PostgreSQL to Neon with FastAPI & SQLAlchemy

This guide walks you through switching from **local PostgreSQL** to **Neon** while keeping your **SQLAlchemy setup** in FastAPI.

---

---

## **2️⃣ Update Database URL**
Find your `.env` or configuration file and update your **DATABASE_URL**:

### **Local PostgreSQL (Before Switching)**
```ini
DATABASE_URL=postgresql://user:password@localhost:5432/mydatabase
```

### **Neon PostgreSQL (After Switching)**
```ini
DATABASE_URL=postgresql://username:password@ep-xxx-neon.tech:5432/dbname?sslmode=require
```

---

## **3️⃣ Update SQLAlchemy Configuration**
Modify your `database.py` (or wherever you configure SQLAlchemy):

### **For Async SQLAlchemy**
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Dependency to get a DB session
async def get_db():
    async with SessionLocal() as session:
        yield session
```

✅ **If using Sync SQLAlchemy** (instead of Async):
```python
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

---

## **4️⃣ Apply Migrations (if using Alembic)**
If you use **Alembic** for database migrations:

1. Update `alembic.ini`:
   ```ini
   sqlalchemy.url = postgresql://username:password@ep-xxx-neon.tech:5432/dbname?sslmode=require
   ```
2. Run migrations:
   ```sh
   alembic upgrade head
   ```

---

## **5️⃣ Test Connection**
Run a simple test with FastAPI:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

app = FastAPI()

@app.get("/")
async def root(db: AsyncSession = Depends(get_db)):
    result = await db.execute("SELECT 'Connected to Neon!'")
    return {"message": result.scalar()}
```

Start your FastAPI app and visit `http://127.0.0.1:8000/`. You should see:
```json
{"message": "Connected to Neon!"}
```

---

## **6️⃣ Deploy (Optional)**
If deploying on a cloud platform:
- Ensure your **Neon database allows external connections**.
- Use **environment variables (`DATABASE_URL`)** for security.

---

🎉 Now you're fully switched to **Neon**, working just like your local PostgreSQL with **SQLAlchemy in FastAPI**! 🚀

