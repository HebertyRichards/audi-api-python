from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional


class FollowStatsResponse(BaseModel):
    followers_count: int
    following_count: int
    is_following: Optional[bool] = None


class followerProfile(BaseModel):
    username: str
    role: str
    avatar_url: Optional[HttpUrl] = None


class FollowingStatsResponse(BaseModel):
    is_following: bool = Field(..., alias="isFollowing")

    class Config:
        populate_by_name = True


class GenericMessageResponse(BaseModel):
    message: str
