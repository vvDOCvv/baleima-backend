from typing import Annotated
from starlette import status
from fastapi import HTTPException, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import get_async_session
from database.models import User
from auth.services import get_current_user
from .services import get_current_admin_cooke
from config import TEMPLATES_DIR


db_dependency = Annotated[AsyncSession, Depends(get_async_session)]
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

async def is_superuser_cooke(user: Annotated[dict, Depends(get_current_admin_cooke)], db: Annotated[AsyncSession, Depends(get_async_session)]):
    if not user:
        return False

    stmt = select(User).filter(User.username == user['username'])
    user_db: Result = await db.execute(stmt)

    user: User | None = user_db.scalars().first()

    if not user or not user.is_superuser:
        return False
    return user


async def is_superuser(user: Annotated[dict, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_async_session)]):
    stmt = select(User).filter(User.username == user['username'])
    user_db: Result = await db.execute(stmt)

    user: User | None = user_db.scalars().first()

    if not user or not user.is_superuser:
         raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Вы не суперпользователь")
    return user


super_user_dependency = Annotated[User, Depends(is_superuser_cooke)]
