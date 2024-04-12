from typing import Annotated
from starlette import status
from fastapi import Depends, HTTPException
from common.dependencies import UOWDep
from auth.schemas import UserAuthSchema
from user.schemas import UserSchema
from database.services.users import UsersService
from auth.services import get_current_user


user_dependency = Annotated[UserAuthSchema, Depends(get_current_user)]


async def has_api_keys(user: user_dependency, uow: UOWDep):
    user: dict | None = await UsersService().get_user(uow, user.username)

    if not user or not user["mexc_api_key"] or not user["mexc_secret_key"]:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="У вас нету ключи MEXC API")
    return UserSchema(**user)


user_has_api_keys = Annotated[UserAuthSchema, Depends(has_api_keys)]
