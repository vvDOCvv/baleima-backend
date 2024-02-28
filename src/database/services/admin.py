from database.utils.unitofwork import IUnitOfWork
from database.models import User
from user.schemas import UserSchema


class AdminService:
    async def get_trades_info(self, uow: IUnitOfWork, limit: int, offset: int):
        async with uow:
            trades: list | None = await uow.trades.find_all(limit=limit, offset=offset)
            total_profit = await uow.trades.get_total_profit()
            count_trades = await uow.trades.get_trades_count()

            return {
                "trades": [trade.to_dict() for trade in trades if trades],
                "total_profit": total_profit if total_profit else 0,
                "count_trades": count_trades if count_trades else 0,
            }


    async def get_user(self, uow: IUnitOfWork, user_id: int):
        async with uow:
            user: User | None = await uow.users.find_one(pk=user_id)
            return user.to_dict() if user else {}


    async def get_users(self, uow: IUnitOfWork):
        async with uow:
            users: list = await uow.users.find_all()
            return [UserSchema(**i.to_dict()) for i in users]


    async def get_user_info(self, uow: IUnitOfWork, user_id: int):
        async with uow:
            user = await uow.users.find_one(pk=user_id)

            if not user:
                return False

            user_profit = await uow.trades.get_user_profit(user_id=user_id)
            user_trades = await uow.trades.get_user_trades(user_id=user_id, limit=20, offset=0)
            user_trades_count = await uow.trades.get_user_trades_count(user_id=user_id)

            return {
                "user": UserSchema(**user.to_dict()),
                "total_profit": user_profit if user_profit else 0,
                "trades": user_trades if user_trades else [],
                "count_trades": user_trades_count if user_trades_count else 0
            }

    async def delete_user(self, uow: IUnitOfWork, user_id: int):
        async with uow:
            await uow.users.delete(pk=user_id)
            return True

