from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AuthorProfile(BaseModel):
    username: str
    role: str


class CommentCount(BaseModel):
    count: int


class TopicByAuthor(BaseModel):
    title: str
    slug: str
    category: str
    created_in: datetime
    profiles: AuthorProfile
    comentarios: List[CommentCount]


class UseStatsResponse(BaseModel):
    topics_count: int = Field(..., alias="topicsCount")
    topics_per_day: float = Field(..., alias="topicsPerDay")
    topics_percentage: float = Field(..., alias="topicsPercentage")
    last_topic_date: Optional[datetime] = Field(None, alias="lastTopicDate")
    messages_count: int = Field(..., alias="messagesCount")
    messages_per_day: float = Field(..., alias="messagesPerDay")
    messages_percentage: float = Field(..., alias="messagesPercentage")
    last_post_date: Optional[datetime] = Field(None, alias="lastPostDate")
    followers_count: int = Field(..., alias="followersCount")
    member_since: datetime = Field(..., alias="memberSince")
    last_login: Optional[datetime] = Field(None, alias="lastLogin")

    class Config:
        from_attributes = True
