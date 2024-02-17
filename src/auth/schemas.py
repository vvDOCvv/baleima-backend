from pydantic import BaseModel, EmailStr, constr, Field, ConfigDict
from passlib.context import CryptContext


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserRegisterSchema(BaseModel):
    email: EmailStr | None = None
    phone_number: constr(min_length=6, max_length=15) = None
    first_name: constr(strip_whitespace=True) | None = Field(None, min_length=3, max_length=50)
    last_name: constr(strip_whitespace=True) | None = Field(None, min_length=3, max_length=50)
    username: constr(strip_whitespace=True, to_lower=True) = Field(min_length=3, max_length=100)
    password: constr(strip_whitespace=True) = Field(min_length=6)

    def deleted_none_dict(self):
        user_data = {key: val for key, val in self.__dict__.items() if val is not None}
        user_data["password"] = bcrypt_context.hash(self.password)
        return user_data


class AuthSchema(BaseModel):
    username: constr(strip_whitespace=True, to_lower=True) = Field(min_length=3, max_length=100)
    password: str= Field(min_length=6)


class UserAuthSchema(BaseModel):
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str


# class UserResponse(UserRequest):
#     model_config = ConfigDict(from_attributes=True)

