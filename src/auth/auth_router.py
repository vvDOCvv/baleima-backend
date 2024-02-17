from datetime import timedelta
from starlette import status
from fastapi import APIRouter, HTTPException
from .schemas import UserRegisterSchema, Token, AuthSchema
from .services import authenticate_user, create_access_token
from database.models import User
from database.repositories import UserRepository


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def create_new_user(user_request: UserRegisterSchema):
    user: User | None = await UserRepository().find_one(username=user_request.username)

    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такой пользователь уже сущестувет.")

    created_user: User = await UserRepository().create(data=user_request.deleted_none_dict())
    return created_user.to_read()


@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(user_request: AuthSchema):
    user: User = await authenticate_user(username=user_request.username, password=user_request.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не правильный логин или пароль.')
    
    token = create_access_token(user.username, user.id, timedelta(days=30))

    return {"access_token": token, "token_type": "bearer"}
