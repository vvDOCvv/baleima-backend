import logging
import asyncio
from time import time
from aiohttp import ClientSession
from database.utils.unitofwork import UnitOfWork, IUnitOfWork
from database.services.error_msgs import ErrorInfoMsgsService
from database.services.trades import TradeInfoService
from database.services.users import UsersService
from user.schemas import UserSchema
from .mexc_basics import MEXCBasics


class AutoTrade:
    MEXC_URL = "https://api.mexc.com"

    def __init__(self) -> None:
        self.uow: IUnitOfWork = UnitOfWork()

    async def auto_trade_buy(self, user: UserSchema):
        mexc = MEXCBasics(user=user)

        try:
            buy_info = await mexc.buy()

            if "code" in buy_info:
                if buy_info["code"] == 30004:
                    msg = f"У пользователья {user.username} не хватает баланс. {buy_info}"
                    await ErrorInfoMsgsService().add_error_msg(uow=self.uow, msg=msg)
                    await UsersService().update_user(uow=self.uow, user_id=user.id, data={"auto_trade": False})
                    logging.info(msg=msg)
                    return

        except Exception as ex:
            await ErrorInfoMsgsService().add_error_msg(uow=self.uow, msg=str(ex))
            logging.error(f"Unexpected error: {ex}. User: {user.username}")
            return

        await asyncio.sleep(1)

        try:
            order_info = await mexc.get_order_info(order_id=buy_info["orderId"], symbol=user.symbol_to_trade)
        except Exception as ex:
            await ErrorInfoMsgsService().add_error_msg(uow=self.uow, msg=str(ex))
            logging.warning(f"Unexpected error: {ex}")
            return

        buy_price: float = round(float(order_info["cummulativeQuoteQty"]) / float(order_info["origQty"]), 6)

        buy_data = {
            "symbol": user.symbol_to_trade,
            "buy_quantity": float(order_info["origQty"]),
            "cummulative_qoute_qty": float(order_info["cummulativeQuoteQty"]),
            "buy_order_id": order_info["orderId"],
            "buy_price": buy_price,
            "user": user.id,
        }

        return buy_data


    async def auto_trade_sell(self, user: UserSchema, buy_data: dict):
        mexc = MEXCBasics(user=user)
        sell_price: float = round(buy_data["buy_price"] * (1 + (user.trade_percent / 100)), 6)

        try:
            sell_info = await mexc.sell(sell_price = sell_price, executed_qty = buy_data["buy_quantity"])
        except Exception as ex:
            await ErrorInfoMsgsService().add_error_msg(uow=self.uow, msg=ex)
            return

        profit: float = round(buy_data["buy_quantity"] * (float(sell_info["price"]) - buy_data["buy_price"]), 6)

        sell_data = {
            "sell_order_id": sell_info["orderId"],
            "sell_price": sell_price,
            "profit": profit,
            "status": "NEW",
        }
        data = {**buy_data, **sell_data}
        return data


    def make_params(self, users: list):
        parametrs = []

        for user in users:
            if not user["mexc_api_key"] or not user["mexc_secret_key"] or not user["new_trades"]:
                continue

            for new_trade in user["new_trades"]:
                timestamp = int(time() * 1000)
                params = {
                    "symbol": new_trade["symbol"],
                    "orderId": new_trade["sell_order_id"],
                    "recvWindow": 20000
                }
                signature = MEXCBasics.make_signature(secret_key=user["mexc_secret_key"], timestamp=timestamp, params=params)

                params.update({
                    "signature": signature,
                    "timestamp": timestamp,
                    "mexc_api_key": user["mexc_api_key"],
                })
                parametrs.append(params)
        return parametrs


    async def create_task(self, headers: dict, parametr: dict, session: ClientSession):
        async with session.get(url="/api/v3/order", headers=headers, params=parametr) as request:
            return await request.json()


    def create_tasks(self, parametrs: list, session: ClientSession):
        tasks = []
        for parametr in parametrs:
            mexc_api_key = parametr.pop("mexc_api_key")
            headers = {
                "Content-Type": "application/json",
                "x-mexc-apikey": mexc_api_key
            }

            task = asyncio.create_task(self.create_task(headers=headers, parametr=parametr, session=session))
            tasks.append(task)
        return tasks
    

    async def create_current_price_task(self, session: ClientSession, symbol: str):
        async with session.get(url='/api/v3/ticker/price', params={'symbol': symbol}) as response:
            return await response.json()


    async def gather_tasks(self, parametrs: list):
        async with ClientSession(base_url=self.MEXC_URL) as session:
            tasks: list = self.create_tasks(parametrs=parametrs, session=session)
            current_price: dict = self.create_current_price_task(session=session, symbol='KASUSDT')
            task_responses: list = await asyncio.gather(*tasks, current_price)
            return {'current_price': task_responses.pop(-1), 'response': task_responses}


    async def start_auto_trade(self):

        users: list = await TradeInfoService().get_users_new_trades(uow=self.uow)

        for user in users:
            if not user["new_trades"]:
                await self.auto_buy(user = user, ignore_last_tarede = True)

        params: list = self.make_params(users=users)

        responses = await self.gather_tasks(parametrs=params)
        
        if not responses['response']:
            return
        
        status_filled_and_canceled = list(filter(lambda r: r['status'] == 'FILLED' or r['status'] == 'CANCELED', responses['response']))
        if status_filled_and_canceled:
            users = await TradeInfoService().add_filled_and_canceled_to_db(uow=self.uow, filled_and_canceled=status_filled_and_canceled)
        
        await self.buy_in_fall(users=users, current_price=responses['current_price'])


    async def buy_in_fall(self, users: list, current_price: dict):
        for user in users:
            if user['last_trade']['status'] != 'NEW':
                continue

            if user['bif_price_3'] >= float(current_price['price']):
                await self.auto_buy(user=user, ignore_last_tarede=True, write_bif=False)

            elif user['bif_price_2'] >= float(current_price['price']):
                await self.auto_buy(user=user, ignore_last_tarede=True, write_bif=False)

            elif user['bif_price_1'] >= float(current_price['price']):
                await self.auto_buy(user=user, ignore_last_tarede=True, write_bif=False)


    async def auto_buy(self, user: dict, ignore_last_tarede: bool = False, write_bif: bool = True):
        if not ignore_last_tarede:
            last_trade = await TradeInfoService().get_user_last_trade(uow=self.uow, user_id = user["id"])
            if last_trade is None or last_trade["status"] == "NEW":
                return

        buy_info = await self.auto_trade_buy(user=UserSchema(**user))
        if not buy_info:
            return
        
        order_data: dict = await self.auto_trade_sell(user = UserSchema(**user), buy_data = buy_info)
        if not order_data:
            return
        
        if write_bif:
            bif_data: dict = self.calculate_bif(buy_price=order_data['buy_price'], user=user)
            await TradeInfoService().add_trade_and_bif(uow=self.uow, trade_data=order_data, bif_data=bif_data)
            return

        await TradeInfoService().add_trade_and_bif(uow=self.uow, trade_data=order_data)

    
    def calculate_bif(self, buy_price: float, user: dict):
        bif_data = {}
        for i in range(1, 4):
            bif_data[f'bif_price_{str(i)}'] = buy_price - buy_price / 100 * user[f'bif_percent_{str(i)}']
        return bif_data
