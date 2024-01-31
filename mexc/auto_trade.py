import asyncio
from .mexc_basics import MEXCBasics
from database.base import async_session
from database.models import User, TradeInfo
from database.crud import trade_crud
from database.crud.user_crud import get_user_from_db
from database.crud.trade_crud import insert_err_msgs


class AutoTrade(MEXCBasics):
    def __init__(
        self,
        mexc_key: str,
        mexc_secret: str,
        symbol: str,
        user: User,
    ):
        super().__init__(mexc_key, mexc_secret)
        self.symbol = symbol
        self.user = user


    async def auto_trade_buy(self):
        trade_qty = self.user.trade_quantity
        buy_info = await self.buy(trade_qty, self.symbol)

        if 'code' in buy_info:
            raise Exception(f"Not balance or balance < 6. {self.user.username}")

        if 'orderId' not in buy_info:
            raise Exception(f"Can not buy: {buy_info}")

        # asyncio.sleep(2)

        order_info = await self.get_order_info(order_id=buy_info["orderId"], symbol=self.symbol)
        buy_price = round(
            float(order_info["cummulativeQuoteQty"]) / float(order_info["origQty"]), 6
        )

        buy_data = {
            "symbol": self.symbol,
            "buy_quantity": order_info["origQty"],
            "cummulative_qoute_qty": float(order_info["cummulativeQuoteQty"]),
            "buy_order_id": order_info["orderId"],
            "buy_price": buy_price,
            "user": self.user.id,
        }

        await trade_crud.create_new_trade_db(buy_data, async_session)

        return order_info["orderId"]


    async def auto_trade_sell(self, buy_order_id: str):
        trade_info: TradeInfo = await trade_crud.get_trade_by_buy_id_db(buy_order_id, async_session)

        if (
            not trade_info.buy_price
            or trade_info.buy_price == 0.0
            or trade_info.cummulative_qoute_qty == 0
            or not trade_info.cummulative_qoute_qty
        ):
            await self.correct_order(trade_info=trade_info)

        sell_price = await self.calculate_sell_price(buy_price=trade_info.buy_price)

        sell_info = await self.sell(
            symbol=self.symbol,
            sell_price=sell_price,
            executed_qty=trade_info.buy_quantity,
        )

        data = {
            "sell_order_id": sell_info["orderId"],
            "sell_price": sell_price,
            "status": "NEW"
        }
        await trade_crud.update_buy_trade_db(buy_id=buy_order_id, data=data, async_session=async_session)

        return sell_info["orderId"]


    async def calculate_sell_price(self, buy_price: float) -> float:
        user: User = await get_user_from_db(self.user.username, async_session)
        percent = user.trade_percent
        return round(buy_price * (1 + (percent / 100)), 6)


    def calculate_profit(
        self, buy_price: float, sell_price: str, orig_qty: float
    ) -> float:
        return round(orig_qty * (float(sell_price) - buy_price), 6)


    async def correct_order(self, trade_info: TradeInfo):
        buy_order_info = await self.get_order_info(
            symbol=self.symbol, order_id=trade_info.buy_order_id
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

        await trade_crud.update_buy_trade_db(buy_id=trade_info.buy_order_id, data=data, async_session=async_session)


    async def correct_sell_order(self, trade_info: TradeInfo):
        sell_order_info = await self.get_order_info(
            symbol=self.symbol, order_id=trade_info.sell_order_id
        )

        data = {
            "sell_price": sell_order_info['price'],
            "status": sell_order_info['status']
        }

        await trade_crud.update_sell_trade_db(sell_id=trade_info.sell_order_id, data=data, async_session=async_session)


    async def check_db(self):
        user_trades_info = await trade_crud.get_all_trades_by_userid_db(user_id=self.user.id, async_session=async_session)

        print(user_trades_info, '88888888888888888')
        for trade_info in user_trades_info:
            trade_info: TradeInfo

            if (
                not trade_info.buy_price
                or trade_info.buy_price == 0.0
                or trade_info.cummulative_qoute_qty == 0
                or not trade_info.cummulative_qoute_qty
            ):
                await self.correct_order(trade_info=trade_info)

            # if (
            #     not trade_info.sell_price
            #     or trade_info.sell_price == 0.0
            # ):
            #     await self.correct_sell_order(trade_info=trade_info)

            if trade_info.status == "CANCELED" or not trade_info.sell_order_id:
                continue

            if trade_info.status == 'NEW':
                sell_order_info = await self.get_order_info(
                    symbol=self.symbol, order_id=trade_info.sell_order_id
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
                        data = {
                            "profit": profit,
                            "status": sell_order_info["status"]
                        }
                        await trade_crud.update_sell_trade_db(sell_id=sell_order_info['orderId'], data=data, async_session=async_session)

                    case "CANCELED":
                        data = {
                            "status": sell_order_info["status"],
                            "profit": 0
                        }
                        await trade_crud.update_sell_trade_db(sell_id=sell_order_info['orderId'], data=data, async_session=async_session)


    async def auto_trade(self):
        try:
            await self.check_db()

            user: User = await get_user_from_db(username=self.user.username, async_session=async_session)
            auto_trade = user.auto_trade

            if auto_trade:
                buy_order_id = await self.auto_trade_buy()
                sell_order_id = await self.auto_trade_sell(buy_order_id=buy_order_id)

                return sell_order_id

        except Exception as ex:
            await insert_err_msgs(
                msg=f"Exeption at auto trade: {str(ex)}",
                async_session=async_session
            )

