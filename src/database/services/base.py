from database.utils.unitofwork import IUnitOfWork


class BaseService:
    async def get_base_info(self, uow: IUnitOfWork):
        async with uow:
            return await uow.base.get_user_and_trade_count_and_profit_sum()
