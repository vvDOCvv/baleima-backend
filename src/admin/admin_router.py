import math
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Request, status, Query, Path
from fastapi.responses import HTMLResponse
from sqlalchemy import select, delete, func
from sqlalchemy.engine import Result
from database.models import User, TradeInfo, ErrorInfoMsgs
from database.repositories import UserRepository, TradeInfoRepository
from .schemas import UpdateUser, LoginForm
from .services import set_admin_cookie
from .dependencies import super_user_dependency, templates, db_dependency


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
async def login(request: Request):
    try:
        form = LoginForm(request)
        await form.create_user()
        response = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
        validate_user_cooke = await set_admin_cookie(response=response, form_data=form)

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


@router.get("/trade-info", response_class=HTMLResponse)
async def trade_info(
        request: Request,
        is_superuser: super_user_dependency,
        limit: int = Query(100, gt=0, lt=100),
        offset: int = Query(0, gt=0, lt=100),
    ):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    trades = await TradeInfoRepository().find_all(limit=limit, offset=offset)
    total_profit = await TradeInfoRepository().profits()
    count_trades = await TradeInfoRepository().count_trades()

    pages: int = 1
    if count_trades > 100:
        pages = math.ceil(count_trades / 100)

    current_page: int = 1
    if offset > 100:
        current_page = math.floor(offset / 100)

    context = {
        "request": request,
        "trades": trades,
        "admin": is_superuser,
        "count_trades": count_trades,
        "pages": pages,
        "current_page": current_page,
        "total_profit": round(total_profit, 6)
    }

    return templates.TemplateResponse('trade-info.html', context=context)


@router.get("/trade-info/{trade_id}", response_class=HTMLResponse)
async def change_tarde(request: Request, is_superuser: super_user_dependency, trade_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    trade: TradeInfo | None = await TradeInfoRepository().find_one(pk=trade_id)

    return templates.TemplateResponse('trade-change.html', {"request": request, "admin": is_superuser, "trade": trade})


@router.get("/trade-info/delete/{trade_id}", response_class=HTMLResponse)
async def delete_trade(request: Request, is_superuser: super_user_dependency, trade_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    trade_crud = await TradeInfoRepository().delete(pk=trade_id)
    
    return RedirectResponse(url=f"/admin/trade-info", status_code=status.HTTP_302_FOUND)


@router.get("/errors", response_class=HTMLResponse)
async def trade_errors(request: Request, is_superuser: super_user_dependency, db: db_dependency):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    stmt = select(ErrorInfoMsgs)
    err_msgs_db: Result = await db.execute(stmt)
    err_msgs = err_msgs_db.scalars().all()

    return templates.TemplateResponse("error-msgs.html", {"request": request, "admin": is_superuser, "err_msgs": err_msgs})

@router.get("/errors/{err_id}", response_class=HTMLResponse)
async def change_error_msgs(request: Request, is_superuser: super_user_dependency, db: db_dependency, err_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    stmt = select(ErrorInfoMsgs).where(ErrorInfoMsgs.id == err_id)
    err_msg_db: Result = await db.execute(stmt)
    err_msg: ErrorInfoMsgs | None = err_msg_db.scalars().one()

    return templates.TemplateResponse("change-err-msg.html", {"request": request, "admin": is_superuser, "err_msg": err_msg})


@router.get("/errors/delete/{error_id}", response_class=HTMLResponse)
async def delete_error(request: Request, is_superuser: super_user_dependency, db: db_dependency, error_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    stmt = delete(ErrorInfoMsgs).where(ErrorInfoMsgs.id == error_id)
    await db.execute(stmt)
    await db.commit()

    return RedirectResponse(url="/admin/errors", status_code=status.HTTP_302_FOUND)


@router.get("/users", response_class=HTMLResponse)
async def get_users(request: Request, is_superuser: super_user_dependency):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    users: list = await UserRepository().find_all()
    return templates.TemplateResponse("users.html", {"request": request, "admin": is_superuser, "users": users})


@router.get("/users/user/{user_id}", response_class=HTMLResponse)
async def user_info(request: Request, is_superuser: super_user_dependency, user_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    user: User = await UserRepository().find_one(pk=user_id)
    
    if not user:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)
    
    trades = await TradeInfoRepository().get_user_trades(user_id=user_id, limit=20)
    total_profit: int = await TradeInfoRepository().profits(user_id=user_id)
    count_trades: int = await TradeInfoRepository().count_trades(user_id=user_id)

    context = {
        "request": request,
        "admin": is_superuser,
        "user": user,
        "trades": trades,
        "total_profit": total_profit,
        "count_trades": count_trades,
    }

    return templates.TemplateResponse("user-info.html", context=context)


@router.post("/users/user/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(request: Request, is_superuser: super_user_dependency):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    try:
        form = UpdateUser(request)
        user_data: dict = await form.update_user()
        user_id = user_data.pop("user_id")

        updated_user = await UserRepository().update(pk=user_id, data=user_data)

        if not updated_user:
            return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)
    
    except:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


@router.get("/users/user/delete/{username}", response_class=HTMLResponse)
async def delete_user(request: Request, is_superuser: super_user_dependency, username: str):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


@router.get("/login", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})



