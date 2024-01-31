import asyncio
import aiohttp
from mexc.mexc_basics import MEXCBasics
from .auto_trade import AutoTrade
from database.base import async_session
from database.models import User, TradeInfo
from database.crud.user_crud import get_user_by_id_db
from database.crud.trade_crud import select_new_trades, insert_err_msgs, thread_is_active, select_on_off


async def set_params(user_id: int):
    user: User = await get_user_by_id_db(user_id, async_session)

    if not user:
        return

    trade = AutoTrade(
        mexc_key=user.mexc_api_key,
        mexc_secret=user.mexc_secret_key,
        symbol=user.symbol_to_trade,
        user=user,
    )
    await trade.auto_trade()


async def check_mexc():
    try:
        is_on = await select_on_off(async_session)
        await thread_is_active(is_active=True, async_session=async_session)
        while is_on:
            new_trades = await select_new_trades(async_session)

            for i in new_trades:
                user_db: User = await get_user_by_id_db(i.user, async_session)
                mexc = MEXCBasics(mexc_key=user_db.mexc_api_key, mexc_secret=user_db.mexc_secret_key)
                res = await mexc.get_order_info(order_id=i.sell_order_id, symbol=i.symbol)

                status = res.get('status')

                if status == "FILLED" or status == "CANCELED":
                    await set_params(user_db.id)
            await asyncio.sleep(15)
            print('---------')
            is_on = await select_on_off(async_session)
    except Exception as ex:
        await thread_is_active(is_active=False, async_session=async_session)
        await insert_err_msgs(msg=str(ex), async_session=async_session)



def check_mexc_run():
    asyncio.run(check_mexc())



