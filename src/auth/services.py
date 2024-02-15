from datetime import timedelta, datetime
from typing import Annotated
from starlette import status
from fastapi import Depends, HTTPException, Request
from passlib.context import CryptContext
from jose import jwt, JWTError
from database.models import User
from database.crud import UserCRUD
from config import SEKRET_KEY, ALGORITHM


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_token(request: Request):
    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    bearer, token = authorization.split()
    
    if not token or bearer.lower() != "bearer":
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return token


def get_current_user(token: Annotated[str, Depends(get_token)]):
    try:
        payload = jwt.decode(token, SEKRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        username: str = payload.get("sub")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не удалось подтвердить пользователя.")

        return {"id": user_id, "username": username}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не удалось подтвердить пользователя.")


async def authenticate_user(username: str, password: str):
    user_crud = UserCRUD(username=username)
    user_exsists: User | None = await user_crud.get_user()

    if not user_exsists:
        return False

    if not bcrypt_context.verify(password, user_exsists.password):
        return False

    return user_exsists


def create_access_token(username: str, user_id: int, expire_delta: timedelta):
    expires = datetime.utcnow() + expire_delta
    encode = { "id": user_id, "sub": username, "exp": expires}
    return jwt.encode(encode, SEKRET_KEY, ALGORITHM)

