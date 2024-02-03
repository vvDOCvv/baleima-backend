import asyncio
from sqlalchemy import select, update, insert, text
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from mexc.mexc_basics import MEXCBasics
from .auto_trade import AutoTrade
from database.base import get_db, async_session
from database.models import User, TradeInfo, ThreadIsActive, ErrorInfoMsgs


async def set_params(user_id: int, db: AsyncSession):
    stmt = select(User).filter(User.id == user_id)
    user_db: Result = await db.execute(stmt)
    user: User = user_db.scalars().first()

    if not user:
        return

    trade = AutoTrade(
        mexc_key=user.mexc_api_key,
        mexc_secret=user.mexc_secret_key,
        symbol=user.symbol_to_trade,
        user=user,
        db=db
    )
    await trade.auto_trade()


async def check_mexc():
    try:
        async with async_session() as db:
            is_active: Result = await db.execute(text("SELECT trade_is_active.on_off FROM trade_is_active WHERE trade_is_active.id = :id").bindparams(id=1))

            is_on = is_active.scalars().one()

        while is_on:
            async with async_session() as db:
                new_stmt = select(TradeInfo).where(TradeInfo.status == "NEW")
                new_trades_db: Result = await db.execute(new_stmt)
                new_trades = new_trades_db.scalars().all()

            for trade in new_trades:
                async with async_session() as db:
                    get_user_stmt = select(User).where(User.id == trade.user)
                    user_db: Result = await db.execute(get_user_stmt)
                    user: User = user_db.scalars().one()

                mexc = MEXCBasics(mexc_key=user.mexc_api_key, mexc_secret=user.mexc_secret_key)
                res = await mexc.get_order_info(order_id=trade.sell_order_id, symbol=trade.symbol)

                status = res.get('status')

                if status == "FILLED" or status == "CANCELED":
                    async with async_session() as db:
                        await set_params(user.id, db)

            await asyncio.sleep(20)
            print(status, '---------')

            async with async_session() as db:
                on_off_stmt = select(ThreadIsActive.on_off).where(ThreadIsActive.id==1)
                is_active: Result = await db.execute(on_off_stmt)
                is_on = is_active.scalars().one()

    except Exception as ex:
        async with async_session() as db:
            stmt_off = update(ThreadIsActive).where(ThreadIsActive.id == 1).values(is_active=False)
            err_stmt = insert(ErrorInfoMsgs).values(error_msg=str(ex))
            await db.execute(err_stmt)
            await db.execute(stmt_off)
            await db.commit()


def check_mexc_run():
    asyncio.run(check_mexc())



