from sqlalchemy import (
    Column,
    Text,
    Integer,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM as SQLAlchemyEnum
from .base import Base, UserRole


class CategoryCommentPermission(Base):
    __tablename__ = "category_comment_permissions"
    __table_args__ = (
        UniqueConstraint(
            "category_slug", "user_role", name="unique_permission_comment"
        ),
        {"schema": "public"},
    )
    id = Column(Integer, primary_key=True)
    category_slug = Column(
        Text, ForeignKey("public.categorias.slug", ondelete="CASCADE"), nullable=False
    )
    user_role = Column(
        SQLAlchemyEnum(UserRole, name="user_role", create_type=False), nullable=False
    )
