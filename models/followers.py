from sqlalchemy import Column, DateTime, ForeignKey, CheckConstraint, UUID
from sqlalchemy.sql import func
from .base import Base


class Follower(Base):
    __tablename__ = "followers"
    __table_args__ = (
        CheckConstraint("follower_id <> following_id", name="check_not_following_self"),
        {"schema": "public"},
    )
    follower_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    following_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
