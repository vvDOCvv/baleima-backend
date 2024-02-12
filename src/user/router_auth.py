from datetime import timedelta
from typing import Annotated
from starlette import status
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError
from .schemas import UserRegistration, Token, UserAuth
from .service import authenticate_user, create_access_token, get_current_user
from dependencies import bcrypt_context, db_dependency
from database.models import User
from fastapi.security import OAuth2PasswordRequestForm, OAuth2, OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer


router = APIRouter(prefix="/auth", tags=["auth"])

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def create_user(user_request: UserRegistration, db: db_dependency):
    stmt = select(User).filter(User.username == user_request.username)
    user: Result = await db.execute(stmt)
    user_exsists: str | None =  user.scalar() is not None

    if user_exsists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такой пользователь уже сущестувет.")

    new_user = User(
        username=user_request.username.lower(),
        email=user_request.email,
        phone_number=user_request.phone_number,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        password=bcrypt_context.hash(user_request.password),
    )
    db.add(new_user)
    
    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не удалось создать пользователя.')


# @router.post("/token", response_model=Token)
# async def login_for_access_token(form_data: Annotated[OAuth2AuthorizationCodeBearer, Depends()], db: db_dependency):
#     user: User | None = await authenticate_user(form_data.username, form_data.password, db)

#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не правильный логин или пароль.')

#     token = create_access_token(user.username, user.id, timedelta(days=30))

#     return {"access_token": token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
async def login_for_access_token(user_request: UserAuth, db: db_dependency):
    user: User = await authenticate_user(username=user_request.username, password=user_request.password, db=db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не правильный логин или пароль.')
    
    token = create_access_token(user.username, user.id, timedelta(days=30))

    return {"access_token": token, "token_type": "bearer"}