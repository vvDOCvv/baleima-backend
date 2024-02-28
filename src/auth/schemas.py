from pydantic import BaseModel, EmailStr, constr, Field, field_validator
from passlib.context import CryptContext


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class RegistrationSchema(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, min_length=6, max_length=15)
    first_name: str | None = Field(default=None, min_length=3, max_length=50)
    last_name: str | None = Field(default=None, min_length=3, max_length=50)
    username: constr(to_lower=True) = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6)


    @field_validator("phone_number", "first_name", "last_name", "username", "password")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if v else v


    @field_validator("password")
    @classmethod
    def hash_password(cls, v: str) -> str:
        return bcrypt_context.hash(v)


class AuthTokenSchema(BaseModel):
    username: constr(strip_whitespace=True, to_lower=True) = Field(min_length=3, max_length=100)
    password: constr(strip_whitespace=True)= Field(min_length=6)


class UserAuthSchema(BaseModel):
    id: int
    username: str
    password: str | None = None

    mexc_api_key: str | None = None
    mexc_secret_key: str | None = None
    auto_trade: bool | None = None
    symbol_to_trade: str | None = None

    trade_quantity: int | None = None
    trade_percent: float | None = None

    bif_percent_1: float | None = None
    bif_percent_2: float | None = None
    bif_percent_3: float | None = None


class Token(BaseModel):
    access_token: str
    token_type: str

