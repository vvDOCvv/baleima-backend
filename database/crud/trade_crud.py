from sqlalchemy import select, update, insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import NoResultFound
from database.models import User, TradeInfo, ErrorInfoMsgs, ThreadIsActive


async def get_all_trades_by_userid_db(user_id: int, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = select(TradeInfo).where(TradeInfo.user == user_id)
        trade: Result = await session.execute(stmt)

    try:
        return trade.scalars().all()
    except NoResultFound:
        return None


async def get_trade_by_buy_id_db(buy_id: str, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = select(TradeInfo).where(TradeInfo.buy_order_id == buy_id)
        trade: Result = await session.execute(stmt)
    try:
        return trade.scalars().one()
    except NoResultFound:
        return None


async def get_trade_by_sell_id_db(sell_id: str, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = select(TradeInfo).where(TradeInfo.sell_order_id == sell_id)
        trade: Result = await session.execute(stmt)
    try:
        return trade.scalars().one()
    except NoResultFound:
        return None


async def create_new_trade_db(data: dict, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = insert(TradeInfo).values(**data)
        await session.execute(stmt)
        await session.commit()


async def update_buy_trade_db(buy_id: str, data: dict, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = update(TradeInfo).where(TradeInfo.buy_order_id == buy_id).values(**data)
        await session.execute(stmt)
        await session.commit()


async def update_sell_trade_db(sell_id: str, data: dict, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = update(TradeInfo).where(TradeInfo.sell_order_id == sell_id).values(**data)
        await session.execute(stmt)
        await session.commit()


async def set_user_auto_trade_db(user, async_session: async_sessionmaker[AsyncSession], auto_trade: bool):
    async with async_session() as session:
        stmt = update(User).where(User.username == user.get("username")).values(auto_trade=auto_trade)
        await session.execute(stmt)
        await session.commit()


async def thread_is_active(is_active: bool, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = update(ThreadIsActive).where(ThreadIsActive.id == 1).values(is_active=is_active)
        await session.execute(stmt)
        await session.commit()


async def thread_on_off(on_or_off: bool, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = update(ThreadIsActive).where(ThreadIsActive.id == 1).values(on_off=on_or_off)
        await session.execute(stmt)
        await session.commit()


async def select_on_off(async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = select(ThreadIsActive.on_off).where(ThreadIsActive.id==1)
        is_active: Result = await session.execute(stmt)

    try:
        return is_active.scalars().one()
    except NoResultFound:
        return None


async def insert_err_msgs(msg: str, async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = insert(ErrorInfoMsgs).values(error_msg=msg)
        await session.execute(stmt)
        await session.commit()


async def select_is_active(async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = select(ThreadIsActive.is_active).where(ThreadIsActive.id==1)
        is_active: Result = await session.execute(stmt)

    try:
        return is_active.scalars().one()
    except NoResultFound:
        return None


async def select_new_trades(async_session: async_sessionmaker[AsyncSession]):
    async with async_session() as session:
        stmt = select(TradeInfo).where(TradeInfo.status == "NEW")
        new_trades = await session.execute(stmt)
    try:
        return new_trades.scalars().all()
    except NoResultFound:
        return None

