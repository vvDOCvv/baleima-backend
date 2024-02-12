from datetime import timedelta
from typing import Annotated
from starlette import status
from fastapi import Depends, Request, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.engine import Result
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from database.models import User
from database.base import get_async_session
from base_services import get_current_user, create_access_token, authenticate_user
from config import SEKRET_KEY, ALGORITHM


async def login_for_access_token(response: Response, db: AsyncSession, form_data: OAuth2PasswordRequestForm = Depends()):
    user: User = await authenticate_user(form_data.username, form_data.password, db=db)

    if not user:
        return False

    token_expires = timedelta(minutes=60)
    token = create_access_token(username=user.username, user_id=user.id, expire_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


def get_current_admin_cooke(request: Request):
    try:
        token = request.cookies.get("access_token")

        if not token:
            return False

        payload = jwt.decode(token, SEKRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if not username or not user_id:
            return False

        return {"username": username, "id": user_id}

    except JWTError:
        return False


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



