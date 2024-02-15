import math
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Request, status, Query, Path
from fastapi.responses import HTMLResponse
from sqlalchemy import select, delete, func
from sqlalchemy.engine import Result
from database.models import User, TradeInfo, ErrorInfoMsgs
from database.crud import UserCRUD, TradeCRUD
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

    trade_crud = TradeCRUD()

    count_and_tp = await trade_crud.get_count_trades_profit()

    pages: int = 1
    if count_and_tp["count"] > 100:
        pages = math.ceil(count_and_tp["count"] / 100)

    current_page: int = 1
    if offset > 100:
        current_page = math.floor(offset / 100)

    if count_and_tp["total_profit"]:
        total_profit = round(count_and_tp["total_profit"], 6)
    else:
        total_profit = 0

    trades = await trade_crud.get_all_trades(limit=limit, offset=offset)

    context = {
        "request": request,
        "trades": trades,
        "admin": is_superuser,
        "count_trades": count_and_tp["count"],
        "pages": pages,
        "current_page": current_page,
        "total_profit": total_profit
    }

    return templates.TemplateResponse('trade-info.html', context=context)


@router.get("/trade-info/{trade_id}", response_class=HTMLResponse)
async def change_tarde(request: Request, is_superuser: super_user_dependency, trade_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    trade: TradeInfo | None = await TradeCRUD.get_trade_info(trade_id=trade_id)

    return templates.TemplateResponse('trade-change.html', {"request": request, "admin": is_superuser, "trade": trade})


@router.get("/trade-info/delete/{trade_id}", response_class=HTMLResponse)
async def delete_trade(request: Request, is_superuser: super_user_dependency, trade_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    trade_crud = await TradeCRUD.delete_trade(trade_id=trade_id)
    print("deleted", trade_crud, trade_id, '-------------')
    
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

    users = await UserCRUD.get_all_users()
    return templates.TemplateResponse("users.html", {"request": request, "admin": is_superuser, "users": users})


@router.get("/users/user/{user_id}", response_class=HTMLResponse)
async def user_info(request: Request, is_superuser: super_user_dependency, user_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    
    user_crud = UserCRUD(user_id=user_id)
    user: User = await user_crud.get_user()

    if not user:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)

    trade_crud = TradeCRUD(user_id=user_id)
    user_trade_profit = await trade_crud.get_user_trades_profit()

    context = {
        "request": request,
        "admin": is_superuser,
        "user": user,
        "trades": user_trade_profit['trades'],
        "total_profit": user_trade_profit['total_profit']
    }

    return templates.TemplateResponse("user-info.html", context=context)


@router.post("/users/user/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(request: Request, is_superuser: super_user_dependency):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    try:
        form = UpdateUser(request)
        await form.update_user()

        user_data = {
            "email": form.email,
            "phone_number": form.phone_number,
            "first_name": form.first_name,
            "last_name": form.last_name,
            "is_staff": form.is_staff,
            "is_superuser": form.is_superuser,
            "for_free": form.for_free,
            "ban": form.ban,
            "auto_trade": form.auto_trade,
            "trade_quantity": int(form.trade_quantity),
            "trade_percent": float(form.trade_percent),
            "symbol_to_trade": form.symbol_to_trade,
            "mexc_api_key": form.mexc_api_key,
            "mexc_secret_key": form.mexc_secret_key,
        }
        if form.last_paid:
            user_data["last_paid"] = form.last_paid

        user_crud = UserCRUD(username=form.username)
        updated_user: User = await user_crud.update_user(user_data=user_data, is_dict=True)

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



