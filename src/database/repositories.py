from sqlalchemy import select, update, desc, func
from sqlalchemy.engine import Result
from database.models import User, TradeInfo, ErrorInfoMsgs
from database.utils.repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = User

    async def find_by_username(self, username: str):
        stmt = select(self.model).where(self.model.username == username)
        res: Result = await self.session.execute(stmt)
        return res.scalar()

    async def find_all_user_auto_trade_true(self):
        stmt = select(self.model).filter(
            self.model.auto_trade == True,
            self.model.mexc_api_key.isnot(None),
            self.model.mexc_secret_key.isnot(None),
        )
        res: Result = await self.session.execute(stmt)
        return res.scalars().all()
    
    async def set_user_bif(self, username: str, data: dict):
        stmt = update(self.model).where(self.model.username == username).values(**data)
        await self.session.execute(stmt)
        # await self.session.commit()


class TradesInfoRepository(SQLAlchemyRepository):
    model = TradeInfo

    async def get_user_new_trades(self, user_id: int):
        stmt = select(self.model).filter(self.model.status == "NEW", self.model.user == user_id)
        res: Result = await self.session.execute(stmt)
        return res.scalars().all()


    async def get_user_trades(self, user_id: int, limit: int = 100, offset: int = 0):
        stmt = select(self.model).filter(self.model.user == user_id).order_by(desc(self.model.id)).limit(limit).offset(offset)
        res: Result = await self.session.execute(stmt)
        return res.scalars().all()


    async def get_user_last_trade(self, user_id: int):
        stmt = select(self.model).where(self.model.user == user_id).order_by(desc(self.model.id))
        res: Result = await self.session.execute(stmt)
        return res.scalar()


    async def get_user_profit(self, user_id: int):
        stmt = select(func.sum(self.model.profit)).filter(self.model.user == user_id, self.model.status == "FILLED")
        res: Result = await self.session.execute(stmt)
        return res.scalar()


    async def get_total_profit(self):
        stmt = select(func.sum(self.model.profit)).filter(self.model.status == "FILLED")
        res: Result = await self.session.execute(stmt)
        return res.scalar()


    async def get_trades_count(self):
        stmt = select(func.count(self.model.id))
        res: Result = await self.session.execute(stmt)
        return res.scalar()


    async def get_user_trades_count(self, user_id: int):
        stmt = select(func.count(self.model.id)).where(self.model.user == user_id)
        res: Result = await self.session.execute(stmt)
        return res.scalar()


    async def edit_trade_by_buy_id(self, buy_id: str, data: dict):
        stmt = update(self.model).where(self.model.buy_order_id == buy_id).values(**data)
        updated = await self.session.execute(stmt)
        await self.session.commit()
        return updated


    async def edit_trade_by_sell_id(self, sell_id: str, data: dict):
        stmt = update(self.model).where(self.model.sell_order_id == sell_id).values(**data)
        updated = await self.session.execute(stmt)
        await self.session.commit()
        return updated
    

    async def get_all_new_trades(self):
        stmt = select(self.model).filter(self.model.status == "NEW")
        res: Result = await self.session.execute(stmt)
        return res.scalars()


class ErrorInfoMsgsRepository(SQLAlchemyRepository):
    model = ErrorInfoMsgs


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
