import asyncio
from db import engine, Base
import models  # 👈 ensure models are registered with Base


async def init_db():
    try:
        async with engine.begin() as conn:
            # This runs Base.metadata.create_all() in sync mode
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully")
    except Exception as e:
        print("❌ Error creating tables:", e)

if __name__ == "__main__":
    asyncio.run(init_db())
