from datetime import timedelta
from starlette import status
from fastapi import APIRouter, HTTPException
from .schemas import RegistrationSchema, Token, AuthTokenSchema, UserAuthSchema
from .services import authenticate_user, create_access_token
from common.dependencies import UOWDep
from database.services.users import UsersService
from user.schemas import UserSchema


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def create_new_user(user_request: RegistrationSchema, uow: UOWDep):
    user: dict = await UsersService().add_user(uow, user_request.model_dump())

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такой пользователь уже сущестувет.")

    return UserSchema(**user)


@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(user_request: AuthTokenSchema, uow: UOWDep):
    user: UserAuthSchema = await authenticate_user(username=user_request.username, password=user_request.password, uow=uow)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не правильный логин или пароль.')

    token = create_access_token(user.username, user.id, timedelta(days=30))

    return {"access_token": token, "token_type": "bearer"}
