from starlette import status
from fastapi import APIRouter
from typing import Annotated
from starlette import status
from fastapi import APIRouter, HTTPException, Depends
from utils.schemas import UserUpdaeSettings, UserUpdaeRequest
from sqlalchemy import select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import get_db
from mexc.mexc_basics import MEXCBasics
from database.models import User, TradeInfo
from utils.services import get_current_user, has_api_keys
from mexc.trade_services import set_params


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not Found"}}
)

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[AsyncSession, Depends(get_db)]


@router.get("", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):

    stmt = select(User).filter(User.username == user['username'])
    userdb: Result = await db.execute(stmt)

    user_db: User | None = userdb.scalars().first()

    if not user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь не сущестувет.")

    try:
        userd = user_db.__dict__
        del userd['id'], userd['password'], userd['mexc_api_key'], userd['mexc_secret_key']
    except KeyError:
        pass

    return userd


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user_request: UserUpdaeRequest, user: user_dependency, db: db_dependency):
    stmt = update(User).where(User.username == user.get("username")).values(
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        phone_number = user_request.phone_number,
        email = user_request.email,
    )

    await db.execute(stmt)
    await db.commit()


@router.put("/settings", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_settings(user_request: UserUpdaeSettings, user: user_dependency, db: db_dependency):
    stmt = update(User).where(User.username == user.get("username")).values(
        trade_quantity = user_request.trade_quantity,
        auto_trade = user_request.auto_trade,
        trade_percent = user_request.trade_percent,
        mexc_api_key = user_request.mexc_api_key,
        mexc_secret_key = user_request.mexc_secret_key,
    )
    await db.execute(stmt)
    await db.commit()


@router.get("/get-all-trades", status_code=status.HTTP_200_OK)
async def trades(user: user_dependency, db: db_dependency):
    stmt = select(TradeInfo).where(TradeInfo.user == user.get("id"))
    trade: Result = await db.execute(stmt)

    all_trades: TradeInfo | None = trade.scalars().all()

    return all_trades


@router.post("/auto-trade", status_code=status.HTTP_200_OK)
async def start_auto_trade(auto_trade: bool, user: Annotated[User, Depends(has_api_keys)], db: db_dependency):
    stmt = update(User).where(User.username == user.username).values(auto_trade=auto_trade)
    await db.execute(stmt)
    await db.commit()

    if auto_trade:
        await set_params(user_id=user.id, db=db)


@router.get("/balance", status_code=status.HTTP_200_OK)
async def balance(user: Annotated[User, Depends(has_api_keys)], symbol: str | None = None):
    mb = MEXCBasics(mexc_key=user.mexc_api_key, mexc_secret=user.mexc_secret_key)
    try:
        balance = await mb.get_balance(symbol=symbol)
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка на сервере")

    if balance is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильный тикер или у вас нет такой валюты.")

    return balance


# @router.get("/order-info", status_code=status.HTTP_200_OK)
# async def order_info(order_id: str, symbol: str, user: Annotated[User, Depends(has_api_keys)]):
#     mb = MEXCBasics(mexc_key=user.mexc_api_key, mexc_secret=user.mexc_secret_key)
#     try:
#         res = await mb.get_order_info(order_id=order_id, symbol=symbol.upper())
#     except Exception as ex:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка на сервере")

#     if "code" in res:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ордер не существует неправильный тикер или ID")

#     return res


# @router.get("/open-orders", status_code=status.HTTP_200_OK)
# async def open_orders(symbol: str, user: Annotated[User, Depends(has_api_keys)]):
#     mb = MEXCBasics(mexc_key=user.mexc_api_key, mexc_secret=user.mexc_secret_key)
#     try:
#         res = await mb.get_current_open_orders(symbol=symbol.upper())
#     except Exception as ex:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка на сервере")

#     if "code" in res:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ордер не существует неправильный тикер или ID")

#     return res

