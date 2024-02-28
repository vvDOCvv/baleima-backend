import asyncio
import hmac, hashlib
from time import time
from urllib.parse import urlencode, quote
from aiohttp import ClientSession
from database.utils.unitofwork import UnitOfWork, IUnitOfWork
from .auto_trade import AutoTrade
from database.services.auto_trade import AutoTradeService
from database.services.trades import TradeInfoService
from database.services.users import UsersService
from user.schemas import UserSchema


class MakeRequest:
    async def get_user_auto_trade_true(self, uow: IUnitOfWork):
        return await AutoTradeService().get_user_new_trades(uow=uow)


    def make_params(self, users: list):
        parametrs = []

        for user in users:
            if not user["mexc_api_key"] or not user["mexc_secret_key"] or not user["new_trades"]:
                continue

            for new_trade in user["new_trades"]:
                timestamp = int(time() * 1000)
                params = {"symbol": new_trade["symbol"], "orderId": new_trade["sell_order_id"], "recvWindow": 20000}
                signature = self.make_signature(secret_key=user["mexc_secret_key"], timestamp=timestamp, params=params)

                params.update({
                    "signature": signature,
                    "timestamp": timestamp,
                    "mexc_api_key": user["mexc_api_key"],
                })
                parametrs.append(params)
        return parametrs


    @staticmethod
    def make_signature(secret_key: str, timestamp: int, params: dict = None) -> str:
        if params:
            encoded_params = urlencode(params, quote_via=quote)
            msg = f"{encoded_params}&timestamp={timestamp}"
        else:
            msg = f"timestamp={timestamp}"

        secret_key = secret_key.encode("utf-8")
        msg = msg.encode("utf-8")

        return hmac.new(key=secret_key, msg=msg, digestmod=hashlib.sha256).hexdigest()


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


class CheckDB(MakeRequest):
    uow = UnitOfWork()

    async def make_request(self):
        users: list = await self.get_user_auto_trade_true(uow=self.uow)

        for user in users:
            if not user["mexc_api_key"] or not user["mexc_secret_key"]:
                continue

            if not user["new_trades"]:
                trade = AutoTrade(user=UserSchema(**user), uow=self.uow)
                await trade.auto_trade()

        params: list = self.make_params(users=users)

        if params:
            return await self.gather_tasks(parametrs=params)


    async def chek_new_trades_and_update_db(self):
        resposes = await self.make_request()

        if not resposes:
            return None

        for response in resposes:
            match response["status"]:
                case "FILLED":
                    res = await TradeInfoService().edit_trade_by_sell_id(
                        uow=self.uow,
                        sell_id=response["orderId"],
                        data={"status": "FILLED"}
                    )
                    await self.buy(user_id=res["username"])

                case "CANCELED":
                    res = await TradeInfoService().edit_trade_by_sell_id(
                        uow=self.uow,
                        sell_id=response["orderId"],
                        data={"status": "CANCELED", "profit": 0.0}
                    )
                    await self.buy(username=res["username"])


    async def buy(self, username: str):
        user: dict = await UsersService().get_user(uow=self.uow, username=username)
        trade = AutoTrade(mexc_key=user["mexc_api_key"], mexc_secret=user["mexc_secret_key"], user=UserSchema(**user))
        await trade.auto_trade()



