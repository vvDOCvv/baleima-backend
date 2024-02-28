from datetime import timedelta, datetime
from typing import Annotated
from starlette import status
from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from .schemas import UserAuthSchema, bcrypt_context
from database.services.users import UsersService
from config import SEKRET_KEY, ALGORITHM


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

        user_data = {"id": user_id, "username": username}

        return UserAuthSchema(**user_data)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не удалось подтвердить пользователя.")


async def authenticate_user(username: str, password: str, uow):
    user_exsists = await UsersService().get_user(uow, username)

    if not user_exsists:
        return False

    if not bcrypt_context.verify(password, user_exsists["password"]):
        return False

    return UserAuthSchema(**user_exsists)


def create_access_token(username: str, user_id: int, expire_delta: timedelta):
    expires = datetime.utcnow() + expire_delta
    encode = { "id": user_id, "sub": username, "exp": expires}
    return jwt.encode(encode, SEKRET_KEY, ALGORITHM)

