import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, Integer, ForeignKey, UUID
from sqlalchemy.dialects.postgresql import ENUM as SQLAlchemyEnum
from sqlalchemy.sql import func
from .base import Base, UserRole


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "public"}
    id = Column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        primary_key=True,
        default=uuid.uuid4,
    )

    username = Column(String, unique=True, nullable=False)
    website = Column(Text, nullable=True)
    gender = Column(Text, nullable=True)
    birthdate = Column(Date, nullable=True)
    location = Column(Text, nullable=True)
    joined_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_login = Column(DateTime(timezone=True), nullable=True)
    role = Column(
        SQLAlchemyEnum(UserRole, name="user_role", create_type=False),
        nullable=False,
        default=UserRole.VISITANTE,
    )
    facebook = Column(Text, nullable=True)
    instagram = Column(Text, nullable=True)
    discord = Column(Text, nullable=True)
    steam = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)
    followers_count = Column(Integer, nullable=False, default=0)
    following_count = Column(Integer, nullable=False, default=0)
    mensagens_count = Column(Integer, nullable=False, default=0)
