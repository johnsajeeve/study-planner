from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 👇 Change password to your actual Postgres password
DATABASE_URL = "postgresql+asyncpg://postgres:yourpassword@localhost:5432/smartplanner"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
