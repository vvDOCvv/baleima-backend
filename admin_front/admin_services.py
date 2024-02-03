from datetime import timedelta
from typing import Annotated
from starlette import status
from pydantic import BaseModel
from fastapi import Depends, HTTPException, Request, Response, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.engine import Result
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from database.models import User
from database.base import get_db
from config import SEKRET_KEY, ALGORITHM
from utils.services import authenticate_user, create_access_token


templates = Jinja2Templates(directory="templates")

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: str | None = None
        self.password: str | None = None

    async def create_user(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")


async def login_for_access_token(response: Response, db: AsyncSession, form_data: OAuth2PasswordRequestForm = Depends()):
    user: User = await authenticate_user(form_data.username, form_data.password, db=db)

    if not user:
        return False

    token_expires = timedelta(minutes=60)
    token = create_access_token(username=user.username, user_id=user.id, expire_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


def get_current_user_cooke(request: Request):
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


async def is_superuser_cooke(user: Annotated[dict, Depends(get_current_user_cooke)], db: Annotated[AsyncSession, Depends(get_db)]):
    if not user:
        return False

    stmt = select(User).filter(User.username == user['username'])
    user_db: Result = await db.execute(stmt)

    user: User | None = user_db.scalars().first()

    if not user or not user.is_superuser:
        return False
    return user



