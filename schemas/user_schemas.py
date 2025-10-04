from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class AllUsersProfile(BaseModel):
    username: str
    role: str
    joined_at: datetime
    last_login: Optional[datetime] = None
    avatar_url: Optional[HttpUrl] = None
    mensagens_count: int


class AllUserResponse(BaseModel):
    data: List[AllUsersProfile]
    total_count: int


class Config:
    from_attributes = True
