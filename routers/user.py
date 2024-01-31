from starlette import status
from fastapi import APIRouter
from typing import Annotated
from starlette import status
from fastapi import APIRouter, HTTPException, Depends
from utils.schemas import UserUpdaeSettings, UserUpdaeRequest
from database.base import async_session
from mexc.mexc_basics import MEXCBasics
from database.models import User
from utils.services import get_current_user, db_keys
from database.crud.user_crud import get_user_from_db, update_user_db, update_user_settings_db
from database.crud.trade_crud import get_all_trades_by_userid_db, set_user_auto_trade_db
from mexc.trade_services import set_params


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not Found"}}
)

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency):
    user_from_db = await get_user_from_db(user['username'], async_session)

    try:
        user_db = user_from_db.__dict__
        del user_db['id'], user_db['password'], user_db['mexc_api_key'], user_db['mexc_secret_key']
    except KeyError:
        pass

    return user_db


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user_request: UserUpdaeRequest, user: user_dependency):
    await update_user_db(user, user_request, async_session)


@router.put("/settings", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_settings(user_request: UserUpdaeSettings, user: user_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Аутентификация не удалась")

    await update_user_settings_db(user, user_request, async_session)


@router.get("/trade-info", status_code=status.HTTP_200_OK)
async def trades(user: user_dependency):
    return await get_all_trades_by_userid_db(user.get('id'), async_session)

@router.post("/auto-trade", status_code=status.HTTP_200_OK)
async def start_auto_trade(auto_trade: bool, user: user_dependency):
    await set_user_auto_trade_db(user, async_session, auto_trade)
    if auto_trade:
        await set_params(user_id=user['id'])


@router.get("/balance", status_code=status.HTTP_200_OK)
async def balance(user: Annotated[User, Depends(db_keys)], symbol: str | None = None):
    mb = MEXCBasics(mexc_key=user.mexc_api_key, mexc_secret=user.mexc_secret_key)
    balance = await mb.get_balance(symbol=symbol)

    if balance is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильный тикер или у вас нет такой валюты.")

    return balance


# @router.get("/current-price", status_code=status.HTTP_200_OK)
# async def current_price(symbol: str):
#     res = await MEXCBasics.get_current_price_by_symbol(symbol=symbol)

#     if "code" in res:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Неправильный тикер")

#     return res


# @router.get("/order-info", status_code=status.HTTP_200_OK)
# async def order_info(order_id: str, symbol: str, user: Annotated[User, Depends(db_keys)]):
#     mb = MEXCBasics(mexc_key=user.mexc_api_key, mexc_secret=user.mexc_secret_key)
#     res = await mb.get_order_info(order_id=order_id, symbol=symbol.upper())

#     if "code" in res:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ордер не существует неправильный тикер или ID")

#     return res


# @router.get("/open-orders", status_code=status.HTTP_200_OK)
# async def open_orders(symbol: str, user: Annotated[User, Depends(db_keys)]):
#     mb = MEXCBasics(mexc_key=user.mexc_api_key, mexc_secret=user.mexc_secret_key)
#     res = await mb.get_current_open_orders(symbol=symbol.upper())

#     if "code" in res:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ордер не существует неправильный тикер или ID")

#     return res

