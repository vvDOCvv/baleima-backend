from datetime import timedelta
from fastapi import Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from database.models import User
from auth.services import create_access_token, authenticate_user
from config import SEKRET_KEY, ALGORITHM


async def set_admin_cookie(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user: User = await authenticate_user(form_data.username, form_data.password)

    if not user:
        return False

    token_expires = timedelta(minutes=60)
    token = create_access_token(username=user.username, user_id=user.id, expire_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


def get_current_admin_cooke(request: Request):
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
