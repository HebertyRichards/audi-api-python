from sqlalchemy import (
    Column,
    Text,
    DateTime,
    Integer,
    ForeignKey,
    CheckConstraint,
    UUID,
)
from sqlalchemy.sql import func
from .base import Base


class Comentario(Base):
    __tablename__ = "comentarios"
    __table_args__ = (
        CheckConstraint("length(content) <= 2000", name="content_length_check"),
        {"schema": "public"},
    )

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    topic_id = Column(
        Integer, ForeignKey("public.topicos.id", ondelete="CASCADE"), nullable=False
    )
    created_in = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_in = Column(DateTime(timezone=True), nullable=True)
