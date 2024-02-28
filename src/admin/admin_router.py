import math
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Request, status, Query, Path
from fastapi.responses import HTMLResponse
from .schemas import UpdateUser, LoginForm
from .services import set_admin_cookie
from .dependencies import super_user_dependency, templates, db_dependency
from common.dependencies import UOWDep
from database.services.admin import AdminService
from database.services.trades import TradeInfoService
from database.services.users import UsersService
from database.services.error_msgs import ErrorInfoMsgsService


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.get("", response_class=HTMLResponse)
async def admin_panel(request: Request, is_superuser: super_user_dependency):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse('admin.html', {"request": request, "admin": is_superuser})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, uow: UOWDep):
    try:
        form = LoginForm(request)
        await form.create_user()
        response = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
        validate_user_cooke = await set_admin_cookie(response=response, form_data=form, uow=uow)

        if not validate_user_cooke:
            msg = 'Incorrect Username or Password'
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

        return response
    except:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Unknown Error"})


@router.get("/logout")
async def logout(request: Request):
    response = templates.TemplateResponse("login.html", {"request": request, "msg": "Logout Successfull"})
    response.delete_cookie(key="access_token")
    return response


@router.get("/trade", response_class=HTMLResponse)
async def trade_info(
        request: Request,
        is_superuser: super_user_dependency,
        uow: UOWDep,
        limit: int = Query(100, gt=0, lt=100),
        offset: int = Query(0, gt=0, lt=100),
    ):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    trades_info = await AdminService().get_trades_info(uow=uow, limit=limit, offset=offset)

    count_trades = int(trades_info["count_trades"]) if trades_info["count_trades"] else 0
    total_profit = int(trades_info["total_profit"]) if trades_info["total_profit"] else 0

    pages: int = 1
    if count_trades > 100:
        pages = math.ceil(count_trades / 100)

    current_page: int = 1
    if offset > 100:
        current_page = math.floor(offset / 100)

    context = {
        "request": request,
        "trades": trades_info["trades"],
        "admin": is_superuser,
        "count_trades": count_trades,
        "pages": pages,
        "current_page": current_page,
        "total_profit": round(total_profit, 6)
    }

    return templates.TemplateResponse('trade-info.html', context=context)


@router.get("/trade/{trade_id}", response_class=HTMLResponse)
async def change_tarde(request: Request, is_superuser: super_user_dependency, uow: UOWDep, trade_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    trade: dict | None = await TradeInfoService().get_trade(uow=uow, trade_id=trade_id)

    return templates.TemplateResponse('trade-change.html', {"request": request, "admin": is_superuser, "trade": trade})


@router.get("/trade/delete/{trade_id}", response_class=HTMLResponse)
async def delete_trade(request: Request, is_superuser: super_user_dependency, uow: UOWDep, trade_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    await TradeInfoService().delete_trade(uow=uow, trade_id=trade_id)

    return RedirectResponse(url=f"/admin/trade-info", status_code=status.HTTP_302_FOUND)


@router.get("/errors", response_class=HTMLResponse)
async def trade_errors(request: Request, is_superuser: super_user_dependency, uow: UOWDep):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    err_msgs = await ErrorInfoMsgsService().get_all_errors(uow=uow)

    return templates.TemplateResponse("error-msgs.html", {"request": request, "admin": is_superuser, "err_msgs": err_msgs})


@router.get("/errors/{error_id}", response_class=HTMLResponse)
async def change_error_msgs(request: Request, is_superuser: super_user_dependency, uow: UOWDep, error_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    err_msg = await ErrorInfoMsgsService().get_all_errors(uow=uow)

    return templates.TemplateResponse("change-err-msg.html", {"request": request, "admin": is_superuser, "err_msg": err_msg})


@router.get("/errors/delete/{error_id}", response_class=HTMLResponse)
async def delete_error(request: Request, is_superuser: super_user_dependency, uow: UOWDep, error_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    await ErrorInfoMsgsService().delete_error_msg(uow=uow, error_id=error_id)

    return RedirectResponse(url="/admin/errors", status_code=status.HTTP_302_FOUND)


@router.get("/users", response_class=HTMLResponse)
async def get_users(request: Request, is_superuser: super_user_dependency, uow: UOWDep):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    users: list = await AdminService().get_users(uow=uow)

    return templates.TemplateResponse("users.html", {"request": request, "admin": is_superuser, "users": users})


@router.get("/users/user/{user_id}", response_class=HTMLResponse)
async def user_info(request: Request, is_superuser: super_user_dependency, uow: UOWDep, user_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    user_info: dict = await AdminService().get_user_info(uow=uow, user_id=user_id)

    if not user_info:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


    context = {
        "request": request,
        "admin": is_superuser,
        "user": user_info["user"],
        "trades": user_info["trades"],
        "total_profit": user_info["total_profit"],
        "count_trades": user_info["count_trades"],
    }

    return templates.TemplateResponse("user-info.html", context=context)


@router.post("/users/user/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(request: Request, is_superuser: super_user_dependency, uow: UOWDep):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    try:
        form = UpdateUser(request)
        user_data: dict = await form.update_user()
        user_id = user_data.pop("user_id")

        updated_user = await UsersService().update_user(uow=uow, user_id=user_id, data=user_data)

        if not updated_user:
            return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)

    except:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


@router.get("/users/user/delete/{user_id}", response_class=HTMLResponse)
async def delete_user(request: Request, is_superuser: super_user_dependency, user_id: int, uow: UOWDep):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    await AdminService().delete_user(uow=uow, user_id=user_id)

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


@router.get("/login", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})



