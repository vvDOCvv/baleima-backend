from typing import Annotated
from datetime import timedelta
from starlette import status
from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import get_async_session
from .schemas import Registration, Token, Auth
from .services import authenticate_user, create_access_token
from database.models import User
from database.crud import UserCRUD


router = APIRouter(prefix="/auth", tags=["auth"])

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db_dependency = Annotated[AsyncSession, Depends(get_async_session)]


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def create_new_user(user_request: Registration):
    user_crud = UserCRUD(username=user_request.username)
    created_user: User | None = await user_crud.create_user(user_data=user_request)

    if not created_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такой пользователь уже сущестувет.")

    return created_user


@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(user_request: Auth):
    user: User = await authenticate_user(username=user_request.username, password=user_request.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не правильный логин или пароль.')
    
    token = create_access_token(user.username, user.id, timedelta(days=30))

    return {"access_token": token, "token_type": "bearer"}
