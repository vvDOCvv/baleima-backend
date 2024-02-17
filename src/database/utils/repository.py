from abc import ABC, abstractmethod
from sqlalchemy import insert, select, update, delete
from sqlalchemy.engine import Result
from database.base import async_session_maker


class AbstractRepository(ABC):
    @abstractmethod
    async def create():
        raise NotImplementedError
    
    @abstractmethod
    async def find_all():
        raise NotImplementedError
    
    @abstractmethod
    async def find_one():
        raise NotImplementedError
    
    @abstractmethod
    async def update():
        raise NotImplementedError
    
    @abstractmethod
    async def delete():
        raise NotImplementedError
    

class SQLAlchemyRepository(AbstractRepository):
    model = None
    
    async def create(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        async with async_session_maker() as session:
            res: Result = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()
        
    
    async def find_all(self, limit: int = 100, offset: int = 0):
        stmt = select(self.model).limit(limit).offset(offset)
        async with async_session_maker() as session:
            res: Result = await session.execute(stmt)
            return res.scalars().all()
        
    
    async def find_one(self, pk: int | None = None, username: str | None = None):
        stmt = None
        if username:
            stmt = select(self.model).where(self.model.username == username)
        else:
            stmt = select(self.model).where(self.model.id == pk)
        
        async with async_session_maker() as session:
            res: Result = await session.execute(stmt)
            return res.scalar()
        

    async def update(self, pk: int, data: dict):
        stmt = update(self.model).where(self.model.id == pk).values(**data).returning(self.model)
        async with async_session_maker() as session:
            res: Result = await session.execute(stmt)
            await session.commit()
            return res.scalar()
        
        
    async def delete(self, pk: int):
        stmt = delete(self.model).where(self.model.id == pk)
        async with async_session_maker() as session:
            await session.execute(stmt)
            await session.commit()
