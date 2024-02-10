from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.engine import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import get_db
from database.models import TradeInfo


router = APIRouter()



@router.get("/")
async def get_basic_info(db: Annotated[AsyncSession, Depends(get_db)]):
    stmt = select(TradeInfo.status).where(TradeInfo.user == 1)
    res: Result = await db.execute(stmt)
    print(res, '---------')

    # stmt = select(func.sum(TradeInfo.profit)).where(TradeInfo.status == "FILLED")
    # res_total_profit: Result = await db.execute(stmt)

    # try:
    #     total_profit = round(res_total_profit.scalar(), 6)
    # except NoResultFound:
    #     total_profit = None

    # return { "total_profit": total_profit }


