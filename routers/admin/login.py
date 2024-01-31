from fastapi import Depends, APIRouter, Request, Response, HTTPException, Form, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/admin"
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: str | None = None
        self.password: str | None = None


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def login(request: Request):
    try:
        fo

