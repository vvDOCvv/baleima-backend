from typing import Annotated
from starlette import status
from datetime import timedelta, datetime
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from sqlalchemy.engine import Result
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt, JWTError
from database.models import User
from database.base import get_async_session
from config import SEKRET_KEY, ALGORITHM


templates = Jinja2Templates(directory="templates")

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SEKRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        username: str = payload.get("sub")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не удалось подтвердить пользователя.")

        return {"id": user_id, "username": username}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не удалось подтвердить пользователя.")


async def authenticate_user(username: str, password: str, db: AsyncSession):
    stmt = select(User).filter(User.username == username)
    user: Result = await db.execute(stmt)

    user_exsists: User | None = user.scalars().first()


    if not user_exsists:
        return False

    if not bcrypt_context.verify(password, user_exsists.password):
        return False

    return user_exsists


def create_access_token(username: str, user_id: int, expire_delta: timedelta):
    encode = { "id": user_id, "sub": username}
    expires = datetime.utcnow() + expire_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SEKRET_KEY, ALGORITHM)


async def has_api_keys(user: Annotated[dict, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_async_session)]):
    stmt = select(User).filter(User.username == user['username'])
    user_db: Result = await db.execute(stmt)

    user: User | None = user_db.scalars().first()

    if not user or not user.mexc_api_key or not user.mexc_secret_key:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="У вас нету ключи MEXC API")
    return user





