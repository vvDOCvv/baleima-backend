from starlette import status
from fastapi import APIRouter
from typing import Annotated
from starlette import status
from fastapi import APIRouter, Depends
from database.base import async_session
from utils.services import is_superuser
from database.crud.trade_crud import select_is_active, thread_on_off
from database.models import User
from mexc.trade_services import check_mexc_run
import threading


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/start-thread", status_code=status.HTTP_200_OK)
async def start_ws(superuser: Annotated[User, Depends(is_superuser)]):
    await thread_on_off(True, async_session)
    th = threading.Thread(target=check_mexc_run, name='check-mexc')
    th.start()


@router.post("/stop-thread", status_code=status.HTTP_200_OK)
async def stop_ws(superuser: Annotated[User, Depends(is_superuser)]):
    await thread_on_off(False, async_session)



@router.get("/thread-is-active", status_code=status.HTTP_200_OK)
async def ws_is_active(superuser: Annotated[User, Depends(is_superuser)]):
    res = await select_is_active(async_session)
