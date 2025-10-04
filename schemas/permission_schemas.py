from pydantic import BaseModel, Field


class TopicPermissionCheckRequest(BaseModel):
    category_slug: str = Field(..., alias="category")


class PermissionResponse(BaseModel):
    allowed: bool

    class Config:
        from_attributes = True
