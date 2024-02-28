import asyncio
from .mexc_basics import MEXCBasics
from database.utils.unitofwork import IUnitOfWork
from database.services.trades import TradeInfoService
from database.services.error_msgs import ErrorInfoMsgsService
from user.schemas import UserSchema


class AutoTrade(MEXCBasics):
    def __init__(self, user: UserSchema, uow: IUnitOfWork):
        super().__init__(user)
        self.user: UserSchema = user
        self.uow: IUnitOfWork = uow


    async def auto_trade_buy(self):
        trade_qty = self.user.trade_quantity

        buy_info = await self.buy(trade_qty, self.user.symbol_to_trade)

        if 'code' in buy_info:
            msg = {"error_msg0": f"{self.user.username}: {buy_info}"}
            try:
                await ErrorInfoMsgsService().add_error_msg(uow=self.uow, msg=msg)
            finally:
                return

        await asyncio.sleep(1)
        order_info = await self.get_order_info(order_id=buy_info["orderId"], symbol=self.user.symbol_to_trade)

        if 'code' in order_info:
            return

        buy_price: float = round(
            float(order_info["cummulativeQuoteQty"]) / float(order_info["origQty"]), 6
        )

        buy_data = {
            "symbol": self.user.symbol_to_trade,
            "buy_quantity": float(order_info["origQty"]),
            "cummulative_qoute_qty": float(order_info["cummulativeQuoteQty"]),
            "buy_order_id": order_info["orderId"],
            "buy_price": buy_price,
            "user": self.user.id,
        }

        return buy_data


    async def auto_trade_sell(self, buy_data: dict):
        sell_price = self.calculate_sell_price(buy_price=buy_data["buy_price"])

        sell_info = await self.sell(
            symbol = self.user.symbol_to_trade,
            sell_price = sell_price,
            executed_qty = buy_data["buy_quantity"],
        )

        profit = self.calculate_profit(
            buy_price = buy_data["buy_price"],
            sell_price = float(sell_info["price"]),
            orig_qty = buy_data["buy_quantity"],
        )

        sell_data = {
            "sell_order_id": sell_info["orderId"],
            "sell_price": sell_price,
            "profit": profit,
            "status": "NEW",
        }

        data = {**buy_data, **sell_data}

        await TradeInfoService().add_trade(uow=self.uow, trade_data=data)

        return data


    def calculate_sell_price(self, buy_price: float) -> float:
        percent = self.user.trade_percent
        return round(buy_price * (1 + (percent / 100)), 6)


    def calculate_profit(self, buy_price: float, sell_price: str, orig_qty: float) -> float:
        return round(orig_qty * (float(sell_price) - buy_price), 6)


    async def correct_order(self, trade_info: dict):
        buy_order_info = await self.get_order_info(
            symbol=self.user.symbol_to_trade, order_id=trade_info["buy_order_id"]
        )

        cummulative_qoute_qty = float(buy_order_info["cummulativeQuoteQty"])
        buy_quantity = float(buy_order_info["origQty"])
        buy_price = round((cummulative_qoute_qty / buy_quantity), 6)

        data = {
            "cummulative_qoute_qty": cummulative_qoute_qty,
            "buy_quantity": buy_quantity,
            "buy_price": buy_price,
            "status": buy_order_info["status"]
        }

        await TradeInfoService().edit_trade_by_buy_id(uow=self.uow, buy_id=trade_info.buy_order_id, trade=data)


    async def correct_sell_order(self, trade_info: dict):
        sell_order_info = await self.get_order_info(
            symbol=self.user.symbol_to_trade, order_id=trade_info["sell_order_id"]
        )

        data = {
            "sell_price": sell_order_info['price'],
            "status": sell_order_info['status']
        }

        await TradeInfoService().edit_trade_by_sell_id(sell_id=trade_info["sell_order_id"], data=data)


    async def check_db(self):
        user_trades_info = await TradeInfoService().get_user_trades(uow=self.uow, user_id=self.user.id)

        if not user_trades_info:
            return

        for trade_info in user_trades_info:
            if not trade_info["buy_order_id"]:
                continue

            if (
                not trade_info["buy_price"]
                or trade_info["buy_price"] == 0.0
                or trade_info["cummulative_qoute_qty"] == 0
                or not trade_info["cummulative_qoute_qty"]
            ):
                await self.correct_order(trade_info=trade_info)

            if trade_info["status"] == "CANCELED" or not trade_info["sell_order_id"]:
                continue

            if (
                not trade_info["sell_price"]
                or trade_info["sell_price"] == 0.0
            ):
                await self.correct_sell_order(trade_info=trade_info)

            if trade_info.status == 'NEW':
                sell_order_info = await self.get_order_info(
                    symbol=self.user.symbol_to_trade, order_id=trade_info.sell_order_id
                )

                if "status" not in sell_order_info:
                    continue

                match sell_order_info["status"]:
                    case "FILLED":
                        trade_info.sell_price = float(sell_order_info["price"])
                        profit = self.calculate_profit(
                            buy_price=trade_info.buy_price,
                            sell_price=sell_order_info["price"],
                            orig_qty=trade_info.buy_quantity,
                        )
                        filled_data = {
                            "profit": profit,
                            "status": sell_order_info["status"]
                        }
                        await TradeInfoService().edit_trade_by_sell_id(uow=self.uow, sell_id=sell_order_info['orderId'], data=filled_data)

                    case "CANCELED":
                        canceled_data = {
                            "status": sell_order_info["status"],
                            "profit": 0
                        }
                        await TradeInfoService().edit_trade_by_sell_id(uow=self.uow, sell_id=sell_order_info['orderId'], data=canceled_data)


    async def auto_trade(self):
        # try:
        await self.check_db()

        last_trade = await TradeInfoService().get_user_last_trade(uow=self.uow, user_id=self.user.id)

        if last_trade:
            last_trade = False if last_trade["status"] == "NEW" else True

        auto_trade = self.user.auto_trade

        if not auto_trade and not last_trade:
            return

        buy_info = await self.auto_trade_buy()

        if buy_info:
            sell_info = await self.auto_trade_sell(buy_data=buy_info)

        # except Exception as ex:
        #     stmt = insert(ErrorInfoMsgs).values(error_msg=str(ex))
        #     async with async_session() as db:
        #         await db.execute(stmt)
        #         await db.commit()

