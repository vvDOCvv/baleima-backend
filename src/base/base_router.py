from starlette import status
from fastapi import APIRouter
from common.dependencies import UOWDep
from .services import BaseService


router = APIRouter(prefix = "", tags = ['base'])


@router.get("/base-info", status_code = status.HTTP_200_OK)
async def get_basic_info(db: UOWDep):
    return BaseService.get_base_info(db)


# @router.get("/test", status_code=status.HTTP_200_OK)
# async def test():
#     trade = AutoTrade()
#     await trade.start_auto_trade()
