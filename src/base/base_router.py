from starlette import status
from fastapi import APIRouter
from database.models import TradeInfo
# from database.repositories import TradeInfoRepository
from database.utils.unitofwork import IUnitOfWork, UnitOfWork
from tasks.tasks import check_db_async
from database.models import Base
from database.base import engine

from auto_trade.auto_trade import AutoTrade

from typing import Annotated


router = APIRouter(prefix="", tags=['base'])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_basic_info():
    # count_and_tp: dict = await TradeInfoRepository()

    # count_trades: int = count_and_tp["count"]
    # total_profit: int | None = round(count_and_tp["total_profit"], 6) if count_and_tp["total_profit"] else 0

    # return {"count": count_trades, "total_profit": total_profit}
    pass


@router.get("/test", status_code=status.HTTP_200_OK)
async def test():
    trade = AutoTrade()
    await trade.start_auto_trade()


@router.get("/create-db")
async def create_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
