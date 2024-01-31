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


class Token(BaseModel):
    access_token: str
    token_type: str


