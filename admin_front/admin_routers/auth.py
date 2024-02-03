from typing import Annotated
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import get_db
from ..admin_services import LoginForm, login_for_access_token


router = APIRouter(
    prefix="",
    tags=["admin"],
    responses={404: {"description": "Not Found"}}
)

templates = Jinja2Templates(directory="templates")
db_dependency = Annotated[AsyncSession, Depends(get_db)]


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    try:
        form = LoginForm(request)
        await form.create_user()
        response = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
        validate_user_cooke = await login_for_access_token(response=response, form_data=form, db=db)

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



