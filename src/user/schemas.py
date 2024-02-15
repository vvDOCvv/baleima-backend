from pydantic import BaseModel, Field, EmailStr, constr


class UpdaeUser(BaseModel):
    email: EmailStr | None = None
    phone_number: constr(min_length=6, max_length=15) | None = None
    first_name: str | None = Field(None, min_length=3, max_length=50)
    last_name: str | None = Field(None, min_length=3, max_length=50)


class UpdaeUserSettings(BaseModel):
    trade_quantity: int = Field(gt=5)
    auto_trade: bool = False
    trade_percent: float = Field(gt=0, lt=1, default=0.3)
    symbol_to_trade: str = Field(min_length=2, max_length=10, default="KASUSDT")
    mexc_api_key: str | None = Field(min_length=5, max_length=50)
    mexc_secret_key: str | None = Field(min_length=5, max_length=100)


class AutoTradeSchema(BaseModel):
    symbol: str = Field(default="KASUSDT")
    auto_trade: bool = Field(default=True)

