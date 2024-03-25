from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, constr, field_validator
from passlib.context import CryptContext


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class Base(BaseModel):
    def deleted_none_dict(self):
        return {key: val for key, val in self.__dict__.items() if val is not None}

    class Config:
        from_attributes = True


class UserUpdateSchema(Base):
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, min_length=8, max_length=15)
    first_name: str | None = Field(default=None, min_length=3, max_length=50)
    last_name: str | None = Field(default=None, min_length=3, max_length=50)
    mexc_api_key: str | None = Field(default=None, min_length=5, max_length=50)
    mexc_secret_key: str | None = Field(default=None, min_length=5, max_length=100)
    symbol_to_trade: str = Field(default="KASUSDT", min_length=2, max_length=15)
    auto_trade: bool = False
    bif_is_active: bool = True
    trade_quantity: int = Field(default=6, gt=5)
    trade_percent: float = Field(default=0.3, gt=0, lt=1)
    bif_percent_1: float = Field(default=3.0, gt=0, lt=50)
    bif_percent_2: float = Field(default=5.0, gt=0, lt=50)
    bif_percent_3: float = Field(default=7.0, gt=0, lt=50)
    password: str | None = Field(default=None, min_length=6)


    @field_validator("phone_number", "first_name", "last_name", "mexc_api_key", "mexc_secret_key", "symbol_to_trade", "password")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if v else v


    @field_validator("password")
    @classmethod
    def hash_password(cls, v: str) -> str:
        return bcrypt_context.hash(v)


class UserSchema(Base):
    id: int
    username: str
    email: str | None
    phone_number: str | None
    first_name: str | None
    last_name: str | None

    is_staff: bool
    is_superuser: bool
    for_free: bool
    ban: bool

    mexc_api_key: str | None
    mexc_secret_key: str | None
    auto_trade: bool
    trade_quantity: int
    trade_percent: float
    symbol_to_trade: str

    bif_is_active: bool
    bif_percent_1: float
    bif_percent_2: float
    bif_percent_3: float
    bif_price_1: float | None
    bif_price_3: float | None
    bif_price_2: float | None
    bif_buy_1: bool
    bif_buy_2: bool
    bif_buy_3: bool

    date_joined: datetime
