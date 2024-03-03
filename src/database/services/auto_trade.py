from database.utils.unitofwork import IUnitOfWork
from database.models import TradeInfo


class AutoTradeService:
    async def get_users_new_trades(self, uow: IUnitOfWork):
        data = []

        async with uow:
            users: list = await uow.users.find_all_user_auto_trade_true()

            for user in users:
                new_trades: list = await uow.trades.get_user_new_trades(user.id)
                user_dict = user.to_dict()
                user_dict["new_trades"] = [new_trade.to_dict() for new_trade in new_trades if new_trades is not None]
                data.append(user_dict)

        return data