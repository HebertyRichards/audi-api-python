from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional
from datetime import datetime, date


class ProfileBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=55)
    website: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[date] = None
    location: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    discord: Optional[str] = None
    steam: Optional[str] = None


class ProfilePublic(ProfileBase):
    joined_at: Optional[datetime]
    last_login: Optional[datetime]
    role: str
    avatar_url: Optional[HttpUrl] = None
    followers_count: int = 0
    following_count: int = 0
    mensagens_count: int = 0


class ProfileUpdate(BaseModel):
    website: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[date] = None
    location: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    discord: Optional[str] = None
    steam: Optional[str] = None


class ProfileDataUpdate(BaseModel):
    username: str = Field(..., min_length=3, max_length=55)
    new_email: EmailStr = Field(..., alias="newEmail")


class AvatarUpdateResponse(BaseModel):
    avatar_url: Optional[HttpUrl] = None


class MessageResponse(BaseModel):
    message: str

    class Config:
        from_attributes = True
