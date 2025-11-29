from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Category(BaseModel):
    slug: str
    name: str
    description: Optional[str] = None


class Author(BaseModel):
    username: str
    avatar_url: Optional[str]
    role: str


class CommentCount(BaseModel):
    count: int


class TopicCategory(BaseModel):
    title: str
    slug: str
    created_in: datetime
    profiles: Author
    comentarios: List[CommentCount]


class paginatedTopics(BaseModel):
    data: List[TopicCategory]
    totalCount: int

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    slug: str
    name: str
    topicRoles: List[str]
    commentRoles: List[str]
    description: Optional[str] = None


class UpdateCategory(BaseModel):
    old_slug: str
    new_slug: str
    name: str
    topicRoles: List[str]
    commentRoles: List[str]
    description: Optional[str] = None
