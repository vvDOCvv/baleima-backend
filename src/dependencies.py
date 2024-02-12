from typing import Annotated
from fastapi import Depends, Request
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import get_async_session


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db_dependency = Annotated[AsyncSession, Depends(get_async_session)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
templates = Jinja2Templates(directory="../templates")
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
token_dependency = Annotated[str, Depends(oauth2_bearer)]




