from sqlalchemy import Column, DateTime, ForeignKey, UUID
from sqlalchemy.sql import func
from .base import Base


class OnlineUser(Base):
    __tablename__ = "online_users"
    __table_args__ = {"schema": "public"}
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    last_seen_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
