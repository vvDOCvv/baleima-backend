from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, constr


class Base(BaseModel):
    def deleted_none_dict(self):
        return {key: val for key, val in self.__dict__.items() if val is not None}
    
    class Config:
        from_attributes = True


class UserUpdateSchema(Base):
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, min_length=8, max_length=15)
    first_name: constr(strip_whitespace=True) | None = Field(default=None, min_length=3, max_length=50)
    last_name: constr(strip_whitespace=True) | None = Field(default=None, min_length=3, max_length=50)
    mexc_api_key: constr(strip_whitespace=True) | None = Field(default=None, min_length=5, max_length=50)
    mexc_secret_key: constr(strip_whitespace=True) | None = Field(default=None, min_length=5, max_length=100)
    symbol_to_trade: constr(strip_whitespace=True) = Field(default="KASUSDT", min_length=2, max_length=15)
    auto_trade: bool = False
    bif_is_active: bool = True
    trade_quantity: int = Field(default=6, gt=5)
    trade_percent: float = Field(default=0.3, gt=0, lt=1)
    bif_percent_1: float = Field(default=3.0, gt=0, lt=50)
    bif_percent_2: float = Field(default=5.0, gt=0, lt=50)
    bif_percent_3: float = Field(default=7.0, gt=0, lt=50)
    # password: constr(strip_whitespace=True) | None = Field(default=None, min_length=6)


class UserSchema(UserUpdateSchema):
    id: int
    username: str
    is_staff: bool
    is_superuser: bool
    for_free: bool
    ban: bool
    last_paid: str | None
    last_login: datetime
    date_joined: datetime

