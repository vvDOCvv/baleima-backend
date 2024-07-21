from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASS


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL)
# engine = create_async_engine(
#     url = "sqlite+aiosqlite:///./athkeeper.db",
#     connect_args = {"check_same_thread": False},
#     echo = True
# )
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

