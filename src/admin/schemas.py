from datetime import datetime
from fastapi import Request
from pydantic import EmailStr


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: str | None = None
        self.password: str | None = None

    async def create_user(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")


class UpdateUser:
    def __init__(self, request: Request) -> None:
        self.request: Request = request
        self.username: str | None = None
        self.email: EmailStr | None = None
        self.phone_number: str | None = None
        self.first_name: str | None = None
        self.last_name: str | None = None
        self.is_superuser: bool | None = None
        self.is_staff: bool | None = None
        self.for_free: bool | None = None
        self.ban: bool | None = None
        self.mexc_api_key: str | None = None
        self.mexc_secret_key: str | None = None
        self.trade_quantity: int | None = None
        self.trade_percent: float | None = None
        self.auto_trade: bool | None = None
        self.symbol_to_trade: str | None = None
        self.last_paid: datetime | None = None

    async def update_user(self):
        form = await self.request.form()
        self.username = form.get("username").strip()
        self.email = form.get("email").strip()
        self.phone_number = form.get("phone_number").strip()
        self.first_name = form.get("first_name").strip()
        self.last_name = form.get("last_name").strip()
        self.is_superuser = True if form.get("is_superuser") else False
        self.is_staff = True if form.get("is_staff") else False
        self.for_free = True if form.get("for_free") else False
        self.ban = True if form.get("ban") else False
        self.mexc_api_key = form.get("mexc_api_key").strip()
        self.mexc_secret_key = form.get("mexc_secret_key").strip()
        self.trade_quantity = form.get("trade_quantity")
        self.trade_percent = form.get("trade_percent")
        self.auto_trade = True if form.get("auto_trade") else False
        self.symbol_to_trade = form.get("symbol_to_trade").upper().strip()
        self.last_paid = datetime.utcnow() if form.get("last_paid") else None
