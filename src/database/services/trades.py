from database.utils.unitofwork import IUnitOfWork
from database.models import TradeInfo


class TradeInfoService:
    async def get_user_trades_count_profit(self, uow: IUnitOfWork, user_id: int, limit: int | None = None, offset: int | None = None):
        async with uow:
            trades = await uow.trades.get_user_trades(user_id=user_id, limit=limit, offset=offset)
            count_trades = await uow.trades.get_user_trades_count(user_id=user_id)
            total_profit = await uow.trades.get_user_profit(user_id=user_id)

        return {
            "trades": trades if trades else [],
            "count_trades": count_trades if count_trades else 0,
            "total_profit": total_profit if total_profit else 0,
        }


    async def add_trade(self, uow: IUnitOfWork, trade_data: dict):
        async with uow:
            trade_id = await uow.trades.create(data=trade_data)
            await uow.commit()
            return trade_id


    async def get_trade(self, uow: IUnitOfWork, trade_id: int):
        async with uow:
            res: TradeInfo = await uow.trades.find_one(pk=trade_id)
        return res.to_dict()


    async def get_user_trades(self, uow: IUnitOfWork, user_id: int):
        async with uow:
            res: list = await uow.trades.get_user_trades(user_id=user_id)
            return [trade.to_dict() for trade in res]


    async def get_user_last_trade(self, uow: IUnitOfWork, user_id: int):
        async with uow:
            res = await uow.trades.get_user_last_trade(user_id=user_id)
            return res.to_dict()


    async def get_trades(self, uow: IUnitOfWork):
        async with uow:
            return await uow.trades.find_all()


    async def edit_trade(self, uow: IUnitOfWork, trade_id: int, trade: dict):
        async with uow:
            await uow.trades.update(pk=trade_id, data=trade)
            await uow.commit()


    async def edit_trade_by_buy_id(self, uow: IUnitOfWork, buy_id: int, data: dict):
        async with uow:
            res = await uow.trades.edit_trade_by_buy_id(buy_id=buy_id, data=data)
            await uow.commit()
            return res.to_dict()


    async def edit_trade_by_sell_id(self, uow: IUnitOfWork, sell_id: int, data: dict):
        async with uow:
            res = await uow.trades.edit_trade_by_sell_id(sell_id=sell_id, data=data)
            await uow.commit()
            return res


    async def delete_trade(self, uow: IUnitOfWork, trade_id: int):
        async with uow:
            await uow.trades.delete(pk=trade_id)
            await uow.commit()

