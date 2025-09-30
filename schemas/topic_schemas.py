from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime


class ProfileNested(BaseModel):
    username: str
    avatar_url: Optional[HttpUrl] = None
    role: str


class ImageNested(BaseModel):
    id: int
    url: HttpUrl


class CommentNested(BaseModel):
    id: int
    content: str
    author_id: str
    topic_id: int
    created_in: datetime
    profiles: ProfileNested


class TopicBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    content: str = Field(..., min_length=10, max_length=10000)


class TopicCreate(TopicBase):
    category_slug: str
    images: Optional[List[HttpUrl]] = None


class TopicUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    content: Optional[str] = Field(None, min_length=10, max_length=10000)


class TopicResponse(TopicBase):
    id: int
    author_id: str
    category: str
    slug: str
    created_in: datetime
    updated_in: Optional[datetime] = None
    profiles: ProfileNested
    imagens: List[ImageNested] = []
    comentarios: List[CommentNested] = []


class TopicPaginatedResponse(BaseModel):
    data: TopicResponse
    totalComments: int


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class CommentCreate(CommentBase):
    images: Optional[List[HttpUrl]] = None


class CommentUpdate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    author_id: str
    topic_id: int
    created_in: datetime
    updated_in: Optional[datetime] = None
    profiles: ProfileNested
    imagens: List[ImageNested] = []

    class Config:
        from_attributes = True
