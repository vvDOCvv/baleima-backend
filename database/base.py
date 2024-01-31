from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .models import Base
from config import settings


engine = create_async_engine("sqlite+aiosqlite:///athkeeper.db", echo=True)

async_session = async_sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)