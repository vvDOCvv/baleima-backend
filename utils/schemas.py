from datetime import datetime
from fastapi import Form, Request
from pydantic import BaseModel, Field, EmailStr, constr, ConfigDict


class UserUpdaeRequest(BaseModel):
    email: EmailStr | None = None
    phone_number: constr(min_length=6, max_length=15) | None = None
    first_name: str | None = Field(None, min_length=3, max_length=50)
    last_name: str | None = Field(None, min_length=3, max_length=50)


class UserRequest(UserUpdaeRequest):
    username: str = Field(min_length=3, max_length=100)
    password: str= Field(min_length=6)


class UserUpdaeSettings(BaseModel):
    trade_quantity: int = Field(gt=5)
    auto_trade: bool
    trade_percent: float
    symbol_to_trade: str
    mexc_api_key: str
    mexc_secret_key: str


# class UserResponse(UserRequest):
#     model_config = ConfigDict(from_attributes=True)


class AdminUpdateUser:
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
        self.username = form.get("username")
        self.email = form.get("email")
        self.phone_number = form.get("phone_number")
        self.first_name = form.get("first_name")
        self.last_name = form.get("last_name")
        self.is_superuser = True if form.get("is_superuser") else False
        self.is_staff = True if form.get("is_staff") else False
        self.for_free = True if form.get("for_free") else False
        self.ban = True if form.get("ban") else False
        self.mexc_api_key = form.get("mexc_api_key")
        self.mexc_secret_key = form.get("mexc_secret_key")
        self.trade_quantity = form.get("trade_quantity")
        self.trade_percent = form.get("trade_percent")
        self.auto_trade = True if form.get("auto_trade") else False
        self.symbol_to_trade = form.get("symbol_to_trade").upper()
        self.last_paid = datetime.utcnow() if form.get("last_paid") else None



class Token(BaseModel):
    access_token: str
    token_type: str


