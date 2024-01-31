from starlette import status
from typing import Annotated
from datetime import timedelta, datetime
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import jwt, JWTError
from database.models import User
from database.crud.user_crud import get_user_from_db
from config import SEKRET_KEY, ALGORITHM
from database.base import async_session


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


async def authenticate_user(username: str, password: str, async_session: async_sessionmaker[AsyncSession]):
    user: User = await get_user_from_db(username.lower(), async_session)

    if not user:
        return False

    if not bcrypt_context.verify(password, user.password):
        return False

    return user


def create_access_token(username: str, user_id: int, expire_delta: timedelta):
    encode = { "id": user_id, "sub": username}
    expires = datetime.utcnow() + expire_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SEKRET_KEY, ALGORITHM)


async def db_keys(user: Annotated[dict, Depends(get_current_user)]):
    user_db: User = await get_user_from_db(user.get("username"), async_session)

    if not user_db or not user_db.mexc_api_key or not user_db.mexc_secret_key:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="У вас нету ключи MEXC API")
    return user_db


async def is_superuser(user: Annotated[dict, Depends(get_current_user)]):
    user_db: User = await get_user_from_db(user.get("username"), async_session)

    if not user_db or not user_db.is_superuser:
         raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Вы не суперпользователь")
    return user_db

