from starlette import status
from fastapi import APIRouter
from database.models import TradeInfo
from database.repositories import TradeInfoRepository

router = APIRouter(prefix="", tags=['base'])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_basic_info():
    count_and_tp: dict = await TradeInfoRepository()
    
    count_trades: int = count_and_tp["count"]
    total_profit: int | None = round(count_and_tp["total_profit"], 6) if count_and_tp["total_profit"] else 0

    return {"count": count_trades, "total_profit": total_profit}

