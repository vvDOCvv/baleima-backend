from datetime import timedelta
from typing import Annotated
from starlette import status
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from utils.schemas import UserRequest, Token
from utils.services import authenticate_user, create_access_token
from database.crud.user_crud import create_new_user
from database.base import async_session
from utils.services import get_current_user
from database.models import User


router = APIRouter(prefix="/auth", tags=["auth"])

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def create_user(user_request: UserRequest):
    created_user: User = await create_new_user(user_request, async_session)

    if not created_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не удалось создать пользователя.')


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(form_data.username, form_data.password, async_session)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не правильный логин или пароль.')

    token = create_access_token(user.username, user.id, timedelta(days=30))

    return {"access_token": token, "token_type": "bearer"}
