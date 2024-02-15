from typing import Annotated
from starlette import status
from fastapi import Depends, HTTPException
from database.models import User
from database.crud import UserCRUD
from auth.services import get_current_user


user_dependency = Annotated[dict, Depends(get_current_user)]


async def has_api_keys(user: Annotated[dict, Depends(get_current_user)]):
    user_crud = UserCRUD(username=user['username'])
    user: User | None = await user_crud.get_user()

    if not user or not user.mexc_api_key or not user.mexc_secret_key:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="У вас нету ключи MEXC API")
    return user


