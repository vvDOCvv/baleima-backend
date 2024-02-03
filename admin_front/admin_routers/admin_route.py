from typing import Annotated
import math
import threading
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, HTTPException, Depends, Request, status, Query, Path, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, update, delete, func
from sqlalchemy.engine import Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import get_db
from database.models import User, ThreadIsActive, TradeInfo, ErrorInfoMsgs
from ..admin_services import is_superuser_cooke
from . import auth
from utils.schemas import AdminUpdateUser
from mexc.trade_services import check_mexc_run


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

router.include_router(auth.router)


templates = Jinja2Templates(directory="templates")
db_dependency = Annotated[AsyncSession, Depends(get_db)]
super_user_dependency = Annotated[User, Depends(is_superuser_cooke)]


@router.get("", response_class=HTMLResponse)
async def admin_panel(request: Request, is_superuser: super_user_dependency, db: db_dependency):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    stmt = select(ThreadIsActive)
    is_active_db: Result = await db.execute(stmt)
    is_active: ThreadIsActive = is_active_db.scalars().one()

    return templates.TemplateResponse('admin.html', {"request": request, "admin": is_superuser, "is_active": is_active})


@router.post("/thread-on-of", response_class=HTMLResponse)
async def on_off_thread(request: Request, is_superuser: super_user_dependency, db: db_dependency, is_active: bool = Form(...)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    if is_active:
        th = threading.Thread(target=check_mexc_run, name='check-mexc')
        th.start()

    stmt = update(ThreadIsActive).where(ThreadIsActive.id == 1).values(is_active=is_active)
    await db.execute(stmt)
    await db.commit()


    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)


@router.get("/trade-info", response_class=HTMLResponse)
async def trade_info(
                    request: Request,
                    is_superuser: super_user_dependency,
                    db: db_dependency,
                    limit: int = Query(100, gt=0),
                    offset: int = 0,
                ):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    count_trades = await db.scalar(func.count(TradeInfo.id))

    pages: int = 1
    if count_trades > 100:
        pages = math.floor(count_trades / 100)

    current_page: int = 1
    if offset >= 100:
        current_page = math.floor(offset / 100)


    stmt = select(TradeInfo).limit(limit).offset(offset).order_by(TradeInfo.date_time.desc())
    trades_db: Result = await db.execute(stmt)
    trades = trades_db.scalars().all()

    context = {
        "request": request,
        "trades": trades,
        "admin": is_superuser,
        "count_trades": count_trades,
        "pages": pages,
        "current_page": current_page
    }

    return templates.TemplateResponse('trade-info.html', context=context)


@router.get("/trade-info/{trade_id}", response_class=HTMLResponse)
async def change_tarde(request: Request, is_superuser: super_user_dependency, db: db_dependency, trade_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    stmt = select(TradeInfo).where(TradeInfo.id == trade_id)
    trade_db: Result = await db.execute(stmt)
    trade: TradeInfo | None = trade_db.scalars().one()

    return templates.TemplateResponse('trade-change.html', {"request": request, "admin": is_superuser, "trade": trade})


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


@router.get("/users", response_class=HTMLResponse)
async def get_users(request: Request, is_superuser: super_user_dependency, db: db_dependency):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    stmt = select(User)
    users_db: Result = await db.execute(stmt)
    users = users_db.scalars().all()

    return templates.TemplateResponse("users.html", {"request": request, "admin": is_superuser, "users": users})


@router.get("/users/user/{user_id}", response_class=HTMLResponse)
async def user_info(request: Request, is_superuser: super_user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    stmt_user = select(User).where(User.id == user_id)
    user_db: Result = await db.execute(stmt_user)
    try:
        user: User = user_db.scalars().one()
    except:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)

    stmt_tarde = select(TradeInfo).where(TradeInfo.user == user_id)
    trades_db: Result = await db.execute(stmt_tarde)
    trades: TradeInfo = trades_db.scalars().all()


    return templates.TemplateResponse("user-info.html", {"request": request, "admin": is_superuser, "user": user, "trades": trades})


@router.post("/users/user/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(request: Request, is_superuser: super_user_dependency, db: db_dependency):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    try:
        form = AdminUpdateUser(request)
        await form.update_user()

        stmt = update(User).where(User.username == form.username).values(
            first_name = form.first_name,
            last_name = form.last_name,
            email = form.email,
            phone_number = form.phone_number,
            is_superuser = form.is_superuser,
            mexc_api_key = form.mexc_api_key,
            mexc_secret_key = form.mexc_secret_key,
            trade_quantity = form.trade_quantity,
            trade_percent = form.trade_percent,
            symbol_to_trade = form.symbol_to_trade,
            auto_trade = form.auto_trade,
            for_free = form.for_free,
            ban = form.ban,
            last_paid = form.last_paid,
            is_staff = form.is_staff,
        )
        await db.execute(stmt)
        await db.commit()

    except:
        return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)

@router.get("/users/user/delete/{username}", response_class=HTMLResponse)
async def delete_user(request: Request, is_superuser: super_user_dependency, db: db_dependency, username: str):
    if not is_superuser:
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    stmt = delete(User).where(User.username == username)
    try:
        await db.execute(stmt)
        await db.commit()
    except:
        pass

    return RedirectResponse(url="/admin/users", status_code=status.HTTP_302_FOUND)


@router.get("/login", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})



