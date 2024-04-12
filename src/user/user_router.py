from starlette import status
from starlette import status
from fastapi import APIRouter, HTTPException
from .schemas import UserUpdateSchema, UserSchema
from auto_trade.mexc_basics import MEXCBasics
from .dependencies import user_dependency, user_has_api_keys
from common.dependencies import UOWDep
from database.services.users import UsersService
from database.services.trades import TradeInfoService
from auto_trade.listen_keys import ListenKeys
from auto_trade.auto_trade import AutoTrade


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"detail": "Not Found"}}
)

@router.get("", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, uow: UOWDep):
    user_db: dict | None = await UsersService().get_user(uow, user.username)

    if not user_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return UserSchema(**user_db)


@router.put("", status_code=status.HTTP_200_OK)
async def update_user(user_request: UserUpdateSchema, user: user_dependency, uow: UOWDep):
    updated_user: dict = await UsersService().update_user(uow=uow, user_id=user.id, data=user_request.deleted_none_dict())

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')

    return UserSchema(**updated_user)


@router.get("/trades", status_code=status.HTTP_200_OK)
async def get_user_trades_and_profit(user: user_dependency, uow: UOWDep, limit: int | None = None, offset: int | None = None):
    return await TradeInfoService().get_user_trades_count_profit(uow, user.id, limit, offset)


@router.post("/trades", status_code=status.HTTP_200_OK)
async def start_auto_trade(auto_trade: bool, user: user_has_api_keys, uow: UOWDep):
    user_mexc = MEXCBasics(user = user)

    try:
        balance: str = await user_mexc.get_balance(symbol="USDT")
        balance = float(balance.get("free"))
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось получить баланса или проверьте провильность API ключа")

    if balance < 6:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Недостаточно USDT для торговли")

    updated_user = await UsersService().update_user(uow, user.id, data={"auto_trade": auto_trade})

    if auto_trade and updated_user:
        return {"detail": f"Ваш торговый бот запущен"}

    return {"detail": f"Ваш торговый бот отключен"}


@router.get("/balance", status_code=status.HTTP_200_OK)
async def balance(user: user_has_api_keys, symbol: str | None = None):
    mb = MEXCBasics(user = user)
    try:
        balance = await mb.get_balance(symbol=symbol)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка на сервере")

    if balance is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильный тикер или у вас нет такой валюты или проверьте провильность API ключа.")

    return balance


@router.get("/listen-key", status_code=status.HTTP_200_OK)
async def get_listen_keys(user: user_has_api_keys):
    get_listen_key = ListenKeys(api_key=user.mexc_api_key, secret_key=user.mexc_secret_key)
    key = await get_listen_key.query_all_listen_keys()

    if not key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при получении ключа")

    return key


@router.put("/listen-key", status_code=status.HTTP_200_OK)
async def keep_alive_listen_key(user: user_has_api_keys, listen_key: str):
    get_listen_key = ListenKeys(api_key=user.mexc_api_key, secret_key=user.mexc_secret_key)
    key = await get_listen_key.keep_alive_listen_key(listen_key=listen_key)

    if not key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при получении ключа")

    return key


@router.delete("/listen-key", status_code=status.HTTP_200_OK)
async def get_listenk_keys(user: user_has_api_keys, listen_key: str):
    get_listen_key = ListenKeys(api_key=user.mexc_api_key, secret_key=user.mexc_secret_key)
    key = await get_listen_key.delete_listen_key(listen_key=listen_key)

    if not key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при получении ключа")

    return key


@router.post("/buy", status_code=status.HTTP_202_ACCEPTED)
async def buy_(user: user_has_api_keys):
    trade = AutoTrade()
    try:
        await trade.auto_buy(user=user.model_dump(), write_bif=True)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Щшибка на сервере или проверьте провильность API ключа")
    
    return {"detail": "Куплено"}


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

