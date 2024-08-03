from database.utils.unitofwork import IUnitOfWork
from database.services.base import BaseService


class BaseService:
    async def get_base_info(uow: IUnitOfWork):
        async with uow:
            return await uow.base.get_user_and_trade_count_and_profit_sum()
