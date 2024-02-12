from typing import Annotated
from starlette import status
from starlette.staticfiles import StaticFiles
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from database.base import get_async_session
from database.models import TradeInfo
from config import STATIC_DIR
from admin import admin_router
from user import user_router, router_auth


app = FastAPI()
app.mount(str("/static"), StaticFiles(directory=str(STATIC_DIR)), name="static")

origins = [
    "https://athkeeper.com",
    "https://www.athkeeper.com",
    "https://api.athkeeper.com",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers = ["Accept", "Accept-Language", "Content-Language", "Content-Type", "Set-Cookie", "Access-Header", "Access-Control-Header", "Authorization"],
)


app.include_router(router_auth.router)
app.include_router(user_router.router)
app.include_router(admin_router.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def get_basic_info(db: Annotated[AsyncSession, Depends(get_async_session)]):
    stmt = select(func.sum(TradeInfo.profit)).where(TradeInfo.status == "FILLED")
    res_total_profit: Result = await db.execute(stmt)

    try:
        total_profit = round(res_total_profit.scalar(), 6)
    except NoResultFound:
        total_profit = None

    return { "total_profit": total_profit }
