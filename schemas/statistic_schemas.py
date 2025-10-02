from pydantic import BaseModel
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
    total_topics: int
    total_comments: int
    recent_topics: List[TopicByAuthor]
    recent_comments: List[TopicByAuthor]

    class Config:
        from_attributes = True
