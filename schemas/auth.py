from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    email_redirect_to: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    keep_logged: bool = False

class UserSession(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str

class PasswordRecovery(BaseModel):
    email: EmailStr

class PasswordChange(BaseModel):
    access_token: str
    new_password: str = Field(..., min_length=6)

class PasswordUpdate(BaseModel):
    new_password: str = Field(..., min_length=6)

class AccountDelete(BaseModel):
    password: str