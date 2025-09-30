from sqlalchemy import (
    Column,
    Text,
    Integer,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM as SQLAlchemyEnum
from .base import Base, UserRole


class CategoryTopicPermission(Base):
    __tablename__ = "category_topic_permissions"
    __table_args__ = (
        UniqueConstraint("category_slug", "user_role", name="unique_permission_topic"),
        {"schema": "public"},
    )
    id = Column(Integer, primary_key=True)
    category_slug = Column(
        Text, ForeignKey("public.categorias.slug", ondelete="CASCADE"), nullable=False
    )
    user_role = Column(
        SQLAlchemyEnum(UserRole, name="user_role", create_type=False), nullable=False
    )
