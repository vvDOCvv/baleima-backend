from starlette import status
from typing import Annotated
from starlette import status
from fastapi import APIRouter, HTTPException, Depends
from .schemas import UserUpdateSchema
from auto_trade.mexc_basics import MEXCBasics
from database.models import User
from .dependencies import user_dependency, has_api_keys
from database.repositories import UserRepository, TradeInfoRepository
from auto_trade.auto_trade import AutoTrade


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"detail": "Not Found"}}
)

@router.get("", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency):
    user_db: User | None = await UserRepository().find_one(username=user.username)

    if not user_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    return user_db.to_read()


@router.put("", status_code=status.HTTP_200_OK)
async def update_user(user_request: UserUpdateSchema, user: user_dependency):
    updated_user: User | None = await UserRepository().update(pk=user.id, data=user_request.deleted_none_dict())

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')

    return updated_user.to_read()


@router.get("/trades", status_code=status.HTTP_200_OK)
async def get_user_trades_and_profit(user: user_dependency, limit: int = 10, offset: int = 0):
    user_trades: list = await TradeInfoRepository().get_user_trades(user_id=user.id, limit=limit, offset=offset)
    user_ptofit: int = await TradeInfoRepository().profits(user_id=user.id)

    return {"user_trades": user_trades, "user_profit": round(user_ptofit, 6)}


@router.post("/trades", status_code=status.HTTP_200_OK)
async def start_auto_trade(auto_trade: bool, user: Annotated[User, Depends(has_api_keys)]):
    updated_user = await UserRepository().update(pk=user.id, data={"auto_trade": auto_trade})
    
    if auto_trade and updated_user:
        trade = AutoTrade(
            mexc_key=user.mexc_api_key,
            mexc_secret=user.mexc_secret_key,
            user=user
        )
        await trade.auto_trade(allow_trade=True)
        return {"detail": f"Ваш торговый бот запущен"}
    
    return {"detail": f"Ваш торговый бот отключен"}


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

