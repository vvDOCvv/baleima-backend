from sqlalchemy import select, Result, func
from utils.repository import SQLAlchemyRepository
from models import User, TradeInfo


class BaseRepository(SQLAlchemyRepository):
    user_model = User
    trade_model = TradeInfo

    async def get_user_and_trade_count_and_profit_sum(self):
        '''Returns { 'users_count: int, trades_count': int, 'trades_profit': float }'''

        query = (
            select(
                func.count(self.user_model.id).label('users_count'),
                (
                    select(func.count(self.trade_model.id))
                    .select_from(self.trade_model)
                ).label('trades_count'),
                (
                    select(func.sum(self.trade_model.profit))
                    .where(self.trade_model.status == 'FILLED')
                    .select_from(self.trade_model)
                ).label('trades_profit')
            )
        )

        res: Result = await self.session.execute(query)
        return res.fetchone()._asdict()
