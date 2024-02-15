from starlette import status
from typing import Annotated
from starlette import status
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from .schemas import UpdaeUserSettings, UpdaeUser, AutoTradeSchema
from mexc.mexc_basics import MEXCBasics
from database.models import User
from database.crud import UserCRUD, TradeCRUD
from .dependencies import user_dependency, has_api_keys
from mexc.auto_trade import AutoTrade


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"detail": "Not Found"}}
)

@router.get("", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency):
    user_crud = UserCRUD(username = user.get("username"))
    user: User | None = await user_crud.get_user()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    return user.to_dict()


@router.put("/update", status_code=status.HTTP_200_OK)
async def update_user(user_request: UpdaeUser, user: user_dependency):
    user_crud = UserCRUD(username=user.get("username"))
    updated_user: User | None = await user_crud.update_user(user_data=user_request)

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')

    return updated_user.to_dict()


@router.put("/update-settings", status_code=status.HTTP_200_OK)
async def update_user_settings(user_request: UpdaeUserSettings, user: user_dependency):
    user_crud = UserCRUD(username=user.get("username"))
    updated_user: User | None = await user_crud.update_user(user_data=user_request)
    
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')

    return updated_user.to_dict()


@router.get("/get-all-trades", status_code=status.HTTP_200_OK)
async def trades(user: user_dependency, limit: int = 10, offset: int = 0):
    trade_crud = TradeCRUD(user_id=user.get("id"))
    trade_and_profit: dict = await trade_crud.get_user_trades_profit(limit=limit, offset=offset)

    return trade_and_profit


@router.post("/auto-trade", status_code=status.HTTP_200_OK)
async def start_auto_trade(set_trade: AutoTradeSchema, user: Annotated[User, Depends(has_api_keys)], background_tasks: BackgroundTasks):
    trade_crud = TradeCRUD(user_id=user.id)
    auto_trade = await trade_crud.set_auto_trade(auto_trade=set_trade.auto_trade)

    if auto_trade:
        trade = AutoTrade(
            mexc_key=user.mexc_api_key,
            mexc_secret=user.mexc_secret_key,
            user=user
        )
        background_tasks.add_task(trade.auto_trade, allow_trade = True)

        return {"detail": f"Ваш торговый бот по {set_trade.symbol.upper()} запущен"}
    
    return {"detail": f"Ваш торговый бот по {set_trade.symbol.upper()} отключен"}


@router.get("/balance", status_code=status.HTTP_200_OK)
async def balance(user: Annotated[User, Depends(has_api_keys)], symbol: str | None = None):
    mb = MEXCBasics(mexc_key=user.mexc_api_key, mexc_secret=user.mexc_secret_key)
    try:
        balance = await mb.get_balance(symbol=symbol)
    except:
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

