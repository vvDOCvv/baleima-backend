from database.utils.unitofwork import IUnitOfWork
from database.models import TradeInfo


class TradeInfoService:
    async def get_users_new_trades(self, uow: IUnitOfWork):
        auto_trade_users = []
        all_new_trades = []

        async with uow:
            auto_trade_users_: list = await uow.users.find_all_user_auto_trade_true()
            all_new_trades_: list = await uow.trades.get_all_new_trades()

            for user in auto_trade_users_:
                user_dict = user.to_dict()
                user_last_trade = await uow.trades.get_user_last_trade(user_id = user_dict['id'])
                user_dict["last_trade"] = user_last_trade.to_dict() if user_last_trade else None
                user_new_trades = await uow.trades.get_user_new_trades(user_id = user_dict['id'])
                user_dict['new_trades'] =  [trade_.to_dict() for trade_ in user_new_trades if user_new_trades is not None]
                auto_trade_users.append(user_dict)
        
            for new_trade in all_new_trades_:
                new_trade_dict = new_trade.to_dict()

                user = await uow.users.find_one(pk = new_trade_dict['user'])
                user_dict = user.to_dict()
                user_dict['new_trade'] = new_trade_dict
                all_new_trades.append(user_dict)
                
        return {'auto_trade_users': auto_trade_users, 'all_new_trades': all_new_trades}
    

    async def add_filled_and_canceled_to_db(self, uow: IUnitOfWork, filled_and_canceled: list):
        users_data = []

        async with uow:        
            for fill_and_can in filled_and_canceled:
                if fill_and_can["status"] == "FILLED":
                    await uow.trades.edit_trade_by_sell_id(sell_id = fill_and_can["orderId"], data = {"status": "FILLED"})
                elif fill_and_can["status"] == "CANCELED":
                    await uow.trades.edit_trade_by_sell_id(sell_id = fill_and_can["orderId"], data = {"status": "CANCELED", "profit": 0.0})
            await uow.commit()

            users: list = await uow.users.find_all_user_auto_trade_true()
            for user in users:
                user_dict = user.to_dict()
                users_data.append(user_dict)
        return users_data


    async def get_user_trades_count_profit(self, uow: IUnitOfWork, user_id: int, limit: int | None = None, offset: int | None = None):
        async with uow:
            trades = await uow.trades.get_user_trades(user_id = user_id, limit = limit, offset = offset)
            count_trades = await uow.trades.get_user_trades_count(user_id = user_id)
            total_profit = await uow.trades.get_user_profit(user_id = user_id)

        return {
            "trades": trades [{trade.to_dict() for trade in trades}] if trades else [],
            "count_trades": count_trades if count_trades else 0,
            "total_profit": total_profit if total_profit else 0,
        }


    async def add_trade_and_bif(self, uow: IUnitOfWork, trade_data: dict, bif_data: dict | None = None):
        async with uow:
            if bif_data:
                await uow.users.update(pk = trade_data['user'], data = bif_data)

            trade_id = await uow.trades.create(data = trade_data)
            return trade_id


    async def get_trade(self, uow: IUnitOfWork, trade_id: int):
        async with uow:
            res: TradeInfo = await uow.trades.find_one(pk = trade_id)
            return res.to_dict()


    async def get_user_trades(self, uow: IUnitOfWork, user_id: int):
        async with uow:
            res: list = await uow.trades.get_user_trades(user_id = user_id)
            return [trade.to_dict() for trade in res]


    async def get_user_last_trade(self, uow: IUnitOfWork, user_id: int):
        async with uow:
            res = await uow.trades.get_user_last_trade(user_id = user_id)
            return res.to_dict()


    async def get_trades(self, uow: IUnitOfWork):
        async with uow:
            return await uow.trades.find_all()


    async def edit_trade(self, uow: IUnitOfWork, trade_id: int, trade: dict):
        async with uow:
            await uow.trades.update(pk = trade_id, data = trade)
            await uow.commit()


    async def edit_trade_by_buy_id(self, uow: IUnitOfWork, buy_id: int, data: dict):
        async with uow:
            res = await uow.trades.edit_trade_by_buy_id(buy_id = buy_id, data = data)
            await uow.commit()
            return res.to_dict()


    async def edit_trade_by_sell_id(self, uow: IUnitOfWork, sell_id: int, data: dict):
        async with uow:
            res = await uow.trades.edit_trade_by_sell_id(sell_id = sell_id, data = data)
            await uow.commit()
            return res


    async def delete_trade(self, uow: IUnitOfWork, trade_id: int):
        async with uow:
            await uow.trades.delete(pk = trade_id)
            await uow.commit()

