from sqlalchemy.ext.asyncio import AsyncSession
from ..database._repositories import BaseRepository


class BaseService:
    @staticmethod
    async def get_base_info(db_session: AsyncSession):
        return await (
            BaseRepository(db_session)
            .get_user_and_trade_count_and_profit_sum()
        )
