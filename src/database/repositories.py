from sqlalchemy import insert, select, update, delete, desc, func
from sqlalchemy.engine import Result
from sqlalchemy.exc import NoResultFound
from database.base import async_session_maker
from database.models import User, TradeInfo, ErrorInfoMsgs
from database.utils.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User


class TradeInfoRepository(SQLAlchemyRepository):
    model = TradeInfo

    async def get_user_trades(self, user_id: int, limit: int = 100, offset: int = 0):
        stmt = (
            select(self.model)
            .where(self.model.user == user_id)
            .order_by(desc(self.model.id))
            .limit(limit)
            .offset(offset)
        )
        async with async_session_maker() as session:
            res: Result = await session.execute(stmt)
            return res.scalars().all()
    
    async def profits(self, user_id: int = None):
        stmt = None
        if user_id:
            stmt = select(func.sum(self.model.profit)).filter(self.model.user == user_id, self.model.status == "FILLED")
        else:
            stmt = select(func.sum(self.model.profit)).filter(self.model.status == "FILLED")

        async with async_session_maker() as session:
            try:
                res: Result = await session.execute(stmt)
                return res.scalar() or 0
            except NoResultFound:
                return 0
            
    async def count_trades(self, user_id: int = None):
        stmt = None
        if user_id:
            stmt = select(func.count(self.model.id)).where(self.model.user == user_id)
        else:
            stmt = select(func.count(self.model.id))
        async with async_session_maker() as session:
            res: Result = await session.execute(stmt)
            return res.scalar()

