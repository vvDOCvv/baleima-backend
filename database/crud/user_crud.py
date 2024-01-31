from starlette import status
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import NoResultFound
from database.models import User
from utils.schemas import UserRequest, UserUpdaeRequest, UserUpdaeSettings


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def user_exists(username, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = select(User).filter(User.username == username)
        user: Result = await session.execute(stmt)
        return user.scalars().first() is not None


async def get_user_by_id_db(user_id: int, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = select(User).filter(User.id == user_id)
        user: Result = await session.execute(stmt)

    try:
        return user.scalars().first()
    except NoResultFound:
        return None


# Auth
async def get_user_from_db(username, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = select(User).filter(User.username == username)
        user: Result = await session.execute(stmt)

    try:
        return user.scalars().first()
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь не сущестувет.")


async def create_new_user(user_request: UserRequest, async_session: async_sessionmaker[AsyncSession]):
    user: str | None = await user_exists(user_request.username.lower(), async_session)

    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такой пользователь уже сущестувет.")

    async with async_session() as session:
        async with session.begin():
            new_user = User(
                username=user_request.username.lower(),
                email=user_request.email,
                phone_number=user_request.phone_number,
                first_name=user_request.first_name,
                last_name=user_request.last_name,
                password=bcrypt_context.hash(user_request.password),
            )
            session.add(new_user)
            await session.commit()
            # await session.refresh(new_user)
            return new_user


# Update user
async def update_user_db(user, user_request: UserUpdaeRequest, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = update(User).where(User.username == user.get("username")).values(
            first_name = user_request.first_name,
            last_name = user_request.last_name,
            phone_number = user_request.phone_number,
            email = user_request.email,
        )
        await session.execute(stmt)
        await session.commit()


# Update user settings
async def update_user_settings_db(user, user_request: UserUpdaeSettings, async_session: async_sessionmaker[AsyncSession]):
    user_db: User | None = await get_user_from_db(user['username'], async_session)

    if user_db is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь не сущестувет.")

    user_db.trade_quantity = user_request.trade_quantity
    user_db.auto_trade = user_request.auto_trade
    user_db.trade_percent = user_request.trade_percent
    user_db.mexc_api_key = user_request.mexc_api_key
    user_db.mexc_secret_key = user_request.mexc_secret_key

    async with async_session() as session:
        session.add(user_db)
        await session.commit()
        # await session.refresh(new_user)

