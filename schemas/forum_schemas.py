from pydantic import BaseModel, HttpUrl
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
    topic_slug: str
    created_in: datetime
    category_name: str
    category_slug: str
    author_username: str
    author_avatar: Optional[HttpUrl] = None
    role: str
    comment_count: int

    class Config:
        from_attributes = True
