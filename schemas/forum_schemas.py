from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NewestMember(BaseModel):
    username: str
    role: str


class ForumStats(BaseModel):
    activeMembers: int
    totalTopics: int
    totalPosts: int
    newestMember: Optional[NewestMember]


class RecentPost(BaseModel):
    id: int
    title: str
    created_in: datetime
    category_name: str
    author_username: str
    author_avatar: Optional[str]
    role: str
    comment_count: int

    class Config:
        from_attributes = True
