import asyncio
from sqlalchemy import select, update, insert, text
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from mexc.mexc_basics import MEXCBasics
from .auto_trade import AutoTrade
from database.base import async_session
from database.models import User, TradeInfo, ThreadIsActive, ErrorInfoMsgs
from urllib.parse import urlencode, quote
import hmac, hashlib
from time import time
import aiohttp
from aiohttp import ClientSession


class MakeRequest:
    async def get_new_trades_from_db(self):
        async with async_session() as db:
            stmt = (
                select(User.mexc_api_key, User.mexc_secret_key, TradeInfo.sell_order_id, TradeInfo.symbol)
                .join(User)
                .filter(TradeInfo.status == "NEW")
            )
            result: Result = await db.execute(stmt)
            return result.mappings().all()


    def make_params(self, new_trades: list):
        parametrs = []
        for new_trade in new_trades:
            timestamp = int(time() * 1000)
            params = {"symbol": new_trade.symbol, "orderId": new_trade.sell_order_id, "recvWindow": 20000}
            signature = self.make_signature(new_trade, params, timestamp)

            params.update({
                "signature": signature,
                "timestamp": timestamp,
                "mexc_api_key": new_trade.mexc_api_key,
            })
            parametrs.append(params)
        return parametrs


    def make_signature(self, trade_db: str, params: dict, timestamp: int) -> str:
        encoded_params = urlencode(params, quote_via=quote)
        msg_for_hmac = f"{encoded_params}&timestamp={timestamp}"
        mexc_secret = trade_db.mexc_secret_key.encode("utf-8")
        msg_for_hmac = msg_for_hmac.encode("utf-8")
        return hmac.new(mexc_secret, msg_for_hmac, hashlib.sha256).hexdigest()


    async def create_task(self, session: ClientSession, headers: dict, parametr: dict):
        async with session.get(url="/api/v3/order", headers=headers, params=parametr) as request:
            return await request.json()


    def create_tasks(self, session: ClientSession, parametrs: list):
        tasks = []
        for parametr in parametrs:
            mexc_api_key = parametr.pop("mexc_api_key")
            headers = {
                "Content-Type": "application/json",
                "x-mexc-apikey": mexc_api_key
            }

            task = asyncio.create_task(self.create_task(session=session, headers=headers, parametr=parametr))
            tasks.append(task)
        return tasks


    async def gather_tasks(self, parametrs: list):
        async with ClientSession(base_url="https://api.mexc.com") as session:
            tasks: list = self.create_tasks(session=session, parametrs=parametrs)
            res = await asyncio.gather(*tasks)
        return res


    async def make_request(self):
        new_trades: list = await self.get_new_trades_from_db()

        if new_trades:
            params: list = self.make_params(new_trades=new_trades)

        if params:
            return await self.gather_tasks(parametrs=params)


class CheckDB(MakeRequest):
    async def chek_new_trades_and_update_db(self):
        resposes = await self.make_request()

        if not resposes:
            return None

        for response in resposes:
            match response["status"]:
                case "FILLED":
                    stmt = (
                        update(TradeInfo)
                        .where(TradeInfo.sell_order_id == response["orderId"])
                        .values(status = "FILLED")
                    ).returning(TradeInfo.user)

                    await self.update_db_and_buy(stmt)

                case "CANCELED":
                    stmt = (
                        update(TradeInfo)
                        .where(TradeInfo.sell_order_id == response["orderId"])
                        .values(status = "CANCELED", profit = 0.0)
                    ).returning(TradeInfo.user)

                    await self.update_db_and_buy(stmt)


    async def update_db_and_buy(self, stmt):
        async with async_session() as db:
            result: Result = await db.execute(stmt)
            user_id = result.scalar()
            await db.commit()

            user_stmt = select(User).where(User.id == user_id)
            user_result: Result = await db.execute(user_stmt)
            user: User = user_result.scalar()

        if user.auto_trade:
            trade = AutoTrade(mexc_key=user.mexc_api_key, mexc_secret=user.mexc_secret_key, user=user)
            await trade.auto_trade()


async def set_params(user_id: int):
    async with async_session() as db:
        stmt = select(User).filter(User.id == user_id)
        user_db: Result = await db.execute(stmt)
        try:
            user: User = user_db.scalars().first()
        except:
            return

    trade = AutoTrade(
        mexc_key=user.mexc_api_key,
        mexc_secret=user.mexc_secret_key,
        user=user,
    )
    await trade.auto_trade()


async def check_mexc():
    try:
        stmt_is_active = select(ThreadIsActive.on_off).where(ThreadIsActive.id==1)
        async with async_session() as db:
            is_active: Result = await db.execute(stmt_is_active)
        is_on = is_active.scalar()


        auto_trade = CheckDB()

        while is_on:
            await auto_trade.chek_new_trades_and_update_db()
            await asyncio.sleep(20)

            stmt_is_active = select(ThreadIsActive.on_off).where(ThreadIsActive.id==1)
            async with async_session() as db:
                is_active: Result = await db.execute(stmt_is_active)
            is_on = is_active.scalar()


    except Exception as ex:
        stmt_off = update(ThreadIsActive).where(ThreadIsActive.id == 1).values(is_active=False)
        err_stmt = insert(ErrorInfoMsgs).values(error_msg=str(ex))
        async with async_session() as db:
            await db.execute(err_stmt)
            await db.execute(stmt_off)
            await db.commit()


def check_mexc_run():
    asyncio.run(check_mexc())



