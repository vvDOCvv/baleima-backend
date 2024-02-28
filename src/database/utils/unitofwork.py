from abc import ABC, abstractmethod
from typing import Type
from database.base import async_session_maker
from database.repositories import UsersRepository, TradesInfoRepository, ErrorInfoMsgsRepository


class IUnitOfWork(ABC):
    users: Type[UsersRepository]
    trades: Type[TradesInfoRepository]
    error_msgs: Type[ErrorInfoMsgsRepository]

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass


class UnitOfWork:
    def __init__(self) -> None:
        self.session_factory = async_session_maker


    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.trades = TradesInfoRepository(self.session)
        self.error_msgs = ErrorInfoMsgsRepository(self.session)


    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()


    async def commit(self):
        await self.session.commit()


    async def rollback(self):
        await self.session.rollback()

