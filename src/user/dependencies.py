from typing import Annotated
from starlette import status
from fastapi import Depends, HTTPException
from database.models import User
from auth.schemas import UserAuthSchema
from database.repositories import UserRepository
from auth.services import get_current_user


user_dependency = Annotated[UserAuthSchema, Depends(get_current_user)]


async def has_api_keys(user: user_dependency):
    user: User | None = await UserRepository().find_one(pk=user.id)

    if not user or not user.mexc_api_key or not user.mexc_secret_key:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="У вас нету ключи MEXC API")
    return user


# def user_service():
#     #  user_service: Annotated[UserService, Depends(user_service)]
#     return UserService(UserRepository)
