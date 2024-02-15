from sqlalchemy.engine import Result
from sqlalchemy import select, insert, update, delete, func, desc
from passlib.context import CryptContext
from .base import async_session_maker
from .models import User, TradeInfo, ErrorInfoMsgs, BuyInFall
from auth.schemas import Registration


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserCRUD:
    def __init__(self, user_id: int | None = None, username: str | None = None) -> None:
        self.user_id: int | None = user_id
        self.username: str | None = username


    async def get_user(self) -> User | None:
        stmt = None
        if self.user_id:
            stmt = select(User).where(User.id == self.user_id)
        else:
            stmt = select(User).where(User.username == self.username)

        async with async_session_maker() as session:
            user: Result = await session.execute(stmt)
            return user.scalar()
    
        
    async def create_user(self, user_data: Registration) -> User | None:
        user_exists = await self.get_user()

        if user_exists:
            return False
         
        stmt = insert(User).values(
            username = user_data.username,
            email = user_data.email,
            phone_number = user_data.phone_number,
            first_name = user_data.first_name,
            last_name = user_data.last_name,
            password = bcrypt_context.hash(user_data.password)
        ).returning(User)

        async with async_session_maker() as session:
            resuslt: Result = await session.execute(stmt)
            await session.commit()
            return resuslt.scalar()
        

    async def update_user(self, user_data, is_dict: bool = False) -> User | None:
        if not is_dict:
            stmt = update(User).where(User.username == self.username).values(user_data.model_dump()).returning(User)
        else:
            stmt = update(User).where(User.username == self.username).values(**user_data).returning(User)
 
        async with async_session_maker() as session:
            res: Result = await session.execute(stmt)
            await session.commit()
            return res.scalar()
        

    async def delete_user(self):
        stmt = delete(User).where(User.username == self.username)
        async with async_session_maker() as session:
            await session.execute(stmt)
            await session.commit()
        

    @staticmethod
    async def get_all_users(limit: int = 100, offset: int = 0):
        stmt = select(User).limit(limit).offset(offset)
        async with async_session_maker() as session:
            res: Result = await session.execute(stmt)
            return res.scalars().all()
        

class TradeCRUD:
    def __init__(self, user_id: int | None = None) -> None:
        self.user_id = user_id

    
    async def get_all_trades(self, limit: int = 100, offset: int = 0):
        stmt = select(TradeInfo).limit(limit).offset(offset).order_by(TradeInfo.id.desc())
        async with async_session_maker() as session:
            trades: Result = await session.execute(stmt)
            return trades.scalars().all()


    async def get_user_trades_profit(self, limit: int = 100, offset: int = 0) -> dict:
        trades_stmt = select(TradeInfo).filter(TradeInfo.user == self.user_id).order_by(desc(TradeInfo.id)).limit(limit).offset(offset)
        profit_stmt = select(func.sum(TradeInfo.profit)).where(TradeInfo.user == self.user_id, TradeInfo.status == "FILLED")

        async with async_session_maker() as session:
            res_trades: Result = await session.execute(trades_stmt)
            res_profit: Result = await session.execute(profit_stmt)

        trades = res_trades.scalars().all()

        try:
            total_profit = round(res_profit.scalar(), 6)
        except:
            total_profit = 0
        
        return {"total_profit": total_profit, "trades": trades}
    

    async def set_auto_trade(self, auto_trade: bool) -> bool:
        stmt = (
            update(User)
            .where(User.id == self.user_id)
            .values(auto_trade=auto_trade)
            .returning(User.auto_trade)
        )

        async with async_session_maker() as session:
            res: Result = await session.execute(stmt)
            await session.commit()
            return res.scalar()
        

    @staticmethod
    async def get_count_trades_profit():
        stmt_tp = select(func.sum(TradeInfo.profit)).where(TradeInfo.status == "FILLED")

        async with async_session_maker() as session:
            count_trades = await session.scalar(func.count(TradeInfo.id))
            res_tp: Result = await session.execute(stmt_tp)

            total_profit = res_tp.scalar()

            return {"count": count_trades, "total_profit": total_profit}


    @staticmethod
    async def get_trade_info(trade_id: int):
        stmt = select(TradeInfo).where(TradeInfo.id == trade_id)
        async with async_session_maker() as session:
            res: Result = await session.execute(stmt)
            return res.scalar()

        
    @staticmethod
    async def delete_trade(trade_id: int):
        stmt = delete(TradeInfo).where(TradeInfo.id == trade_id)
        async with async_session_maker() as session:
            await session.execute(stmt)
            await session.commit()

