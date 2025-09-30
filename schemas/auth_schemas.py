from pydantic import BaseModel, EmailStr, Field
from pydantic.alias_generators import to_camel
from typing import Optional
import uuid


class CamelCaseModel(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True


class UserCreate(CamelCaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    email_redirect_to: Optional[str] = None


class UserLogin(CamelCaseModel):
    email: EmailStr
    password: str
    keep_logged: bool = False


class UserSession(CamelCaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    avatar_url: Optional[str] = None
    role: Optional[str] = None


class PasswordRecovery(CamelCaseModel):
    email: EmailStr


class PasswordChange(CamelCaseModel):
    access_token: str
    new_password: str = Field(..., min_length=6)


class PasswordUpdate(CamelCaseModel):
    new_password: str = Field(..., min_length=6)


class AccountDelete(CamelCaseModel):
    password: str
