import asyncio
from sqlalchemy import text
from db import engine

async def test():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.fetchall())

asyncio.run(test())
