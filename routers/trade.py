from typing import Annotated
import threading
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, Response, Form, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import get_db
from database.models import User, TradeInfo, ThreadIsActive
from utils.services import is_superuser, LoginForm, login_for_access_token


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not Found"}}
)

templates = Jinja2Templates(directory="templates")
db_dependency = Annotated[AsyncSession, Depends(get_db)]
super_user_dependency = Annotated[User, Depends(is_superuser)]

