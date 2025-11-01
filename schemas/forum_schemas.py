from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


class NewestMember(BaseModel):
    username: str
    role: str


class ForumStats(BaseModel):
    activeMembers: int
    totalTopics: int
    totalPosts: int
    newestMember: Optional[NewestMember]


class LastRegistredUser(BaseModel):
    username: str
    role: str
    avatar_url: Optional[HttpUrl] = None
    location: Optional[str] = None
    joined_at: datetime


class OnlineUserProfile(BaseModel):
    username: str
    role: str
    avatar_url: Optional[HttpUrl] = None


class OnlineUser(BaseModel):
    last_seen_at: datetime
    profiles: OnlineUserProfile


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


class DashboardData(BaseModel):

    stats: ForumStats
    recent_posts: List[RecentPost] = Field(..., alias="recentPosts")
    last_user: LastRegistredUser = Field(..., alias="lastUser")
    online_users: List[OnlineUser] = Field(..., alias="onlineUsers")

    class Config:
        populate_by_name = True
