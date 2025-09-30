from pydantic import BaseModel


class TopicPermissionCheckRequest(BaseModel):
    category_slug: str


class PermissionResponse(BaseModel):
    has_permission: bool

    class Config:
        from_attributes = True
