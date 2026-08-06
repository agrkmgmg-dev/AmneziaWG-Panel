import asyncio

from backend.app.db.database import engine
from backend.app.db.base import Base

from backend.app.models.user import User
from backend.app.models.peer import Peer
from backend.app.models.traffic import Traffic
from backend.app.models.activity_log import ActivityLog


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully")


if __name__ == "__main__":
    asyncio.run(create_tables())