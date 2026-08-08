import asyncio
from sqlalchemy import text
from backend.app.db.database import AsyncSessionLocal

async def check_database():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' "
                "AND name='token_revocations'"
            )
        )
        print("token_revocations:", result.scalar())

asyncio.run(check_database())
