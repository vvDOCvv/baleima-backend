from pydantic import BaseModel, EmailStr, constr, Field, ConfigDict


class Registration(BaseModel):
    email: EmailStr | None = None
    phone_number: constr(min_length=6, max_length=15) | None = None
    first_name: str | None = Field(None, min_length=3, max_length=50)
    last_name: str | None = Field(None, min_length=3, max_length=50)
    username: str = Field(min_length=3, max_length=100)
    password: str= Field(min_length=6)


class Auth(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str= Field(min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str


# class UserResponse(UserRequest):
#     model_config = ConfigDict(from_attributes=True)

