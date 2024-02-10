from sqlalchemy import select, update, insert
from sqlalchemy.engine import Result
from database.base import async_session
from .mexc_basics import MEXCBasics
from database.models import User, TradeInfo, ErrorInfoMsgs



class AutoTrade(MEXCBasics):
    def __init__(
        self,
        mexc_key: str,
        mexc_secret: str,
        user: User,
    ):
        super().__init__(mexc_key, mexc_secret)
        self.user = user


    async def auto_trade_buy(self):
        trade_qty = self.user.trade_quantity
        buy_info = await self.buy(trade_qty, self.user.symbol_to_trade)

        if 'code' in buy_info:
            raise Exception(f"Not balance or balance < 6. {self.user.username}: {buy_info}")

        if 'orderId' not in buy_info:
            raise Exception(f"Can not buy: {buy_info}")

        order_info = await self.get_order_info(order_id=buy_info["orderId"], symbol=self.user.symbol_to_trade)
        buy_price = round(
            float(order_info["cummulativeQuoteQty"]) / float(order_info["origQty"]), 6
        )

        buy_data = {
            "symbol": self.user.symbol_to_trade,
            "buy_quantity": order_info["origQty"],
            "cummulative_qoute_qty": float(order_info["cummulativeQuoteQty"]),
            "buy_order_id": order_info["orderId"],
            "buy_price": buy_price,
            "user": self.user.id,
        }

        stmt = insert(TradeInfo).values(**buy_data)
        async with async_session() as db:
            await db.execute(stmt)
            await db.commit()

        return order_info["orderId"]


    async def auto_trade_sell(self, buy_order_id: str):
        stmt = select(TradeInfo).where(TradeInfo.buy_order_id == buy_order_id)
        async with async_session() as db:
            trade_db: Result = await db.execute(stmt)
            trade_info: TradeInfo = trade_db.scalar()

        if (
            not trade_info.buy_price
            or trade_info.buy_price == 0.0
            or trade_info.cummulative_qoute_qty == 0
            or not trade_info.cummulative_qoute_qty
        ):
            await self.correct_order(trade_info=trade_info)

        sell_price = self.calculate_sell_price(buy_price=trade_info.buy_price)

        sell_info = await self.sell(
            symbol=self.user.symbol_to_trade,
            sell_price=sell_price,
            executed_qty=trade_info.buy_quantity,
        )

        profit = self.calculate_profit(
            buy_price=trade_info.buy_price,
            sell_price=sell_info["price"],
            orig_qty=trade_info.buy_quantity,
        )

        data = {
            "sell_order_id": sell_info["orderId"],
            "sell_price": sell_price,
            "profit": profit,
            "status": "NEW"
        }

        stmt = update(TradeInfo).where(TradeInfo.buy_order_id == buy_order_id).values(**data)
        async with async_session() as db:
            await db.execute(stmt)
            await db.commit()

        return sell_info["orderId"]


    def calculate_sell_price(self, buy_price: float) -> float:
        percent = self.user.trade_percent
        return round(buy_price * (1 + (percent / 100)), 6)


    def calculate_profit(self, buy_price: float, sell_price: str, orig_qty: float) -> float:
        return round(orig_qty * (float(sell_price) - buy_price), 6)


    async def correct_order(self, trade_info: TradeInfo):
        buy_order_info = await self.get_order_info(
            symbol=self.user.symbol_to_trade, order_id=trade_info.buy_order_id
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

        stmt = update(TradeInfo).where(TradeInfo.buy_order_id == trade_info.buy_order_id).values(**data)
        async with async_session() as db:
            await db.execute(stmt)
            await db.commit()


    async def correct_sell_order(self, trade_info: TradeInfo):
        sell_order_info = await self.get_order_info(
            symbol=self.user.symbol_to_trade, order_id=trade_info.sell_order_id
        )

        data = {
            "sell_price": sell_order_info['price'],
            "status": sell_order_info['status']
        }

        stmt = update(TradeInfo).where(TradeInfo.sell_order_id == trade_info.sell_order_id).values(**data)
        async with async_session() as db:
            await db.execute(stmt)
            await db.commit()


    async def check_db(self):
        stmt = select(TradeInfo).where(TradeInfo.user == self.user.id)
        async with async_session() as db:
            trade_obj: Result = await db.execute(stmt)
            user_trades_info = trade_obj.scalars().all()

        if not user_trades_info:
            return

        for trade_info in user_trades_info:
            trade_info: TradeInfo

            if (
                not trade_info.buy_price
                or trade_info.buy_price == 0.0
                or trade_info.cummulative_qoute_qty == 0
                or not trade_info.cummulative_qoute_qty
            ):
                await self.correct_order(trade_info=trade_info)

            if (
                not trade_info.sell_price
                or trade_info.sell_price == 0.0
            ):
                await self.correct_sell_order(trade_info=trade_info)

            if trade_info.status == "CANCELED" or not trade_info.sell_order_id:
                continue

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

                        stmt = update(TradeInfo).where(TradeInfo.sell_order_id == sell_order_info['orderId']).values(**filled_data)
                        async with async_session() as db:
                            await db.execute(stmt)
                            await db.commit()

                    case "CANCELED":
                        canceled_data = {
                            "status": sell_order_info["status"],
                            "profit": 0
                        }

                        stmt = update(TradeInfo).where(TradeInfo.sell_order_id == sell_order_info['orderId']).values(**canceled_data)
                        async with async_session() as db:
                            await db.execute(stmt)
                            await db.commit()


    async def auto_trade(self):
        try:
            await self.check_db()

            async with async_session() as db:
                stmt = select(TradeInfo.status).where(TradeInfo.user == self.user.id).order_by(TradeInfo.id.desc)

            auto_trade = self.user.auto_trade

            if auto_trade:
                buy_order_id = await self.auto_trade_buy()
                sell_order_id = await self.auto_trade_sell(buy_order_id=buy_order_id)

                return sell_order_id

        except Exception as ex:
            stmt = insert(ErrorInfoMsgs).values(error_msg=str(ex))
            async with async_session() as db:
                await db.execute(stmt)
                await db.commit()
