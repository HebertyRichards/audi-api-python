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


class Topico(Base):
    __tablename__ = "topicos"
    __table_args__ = (
        CheckConstraint("length(content) <= 2000", name="content_length_check"),
        {"schema": "public"},
    )

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    category = Column(
        Text, ForeignKey("public.categorias.slug", ondelete="RESTRICT"), nullable=False
    )
    created_in = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_in = Column(DateTime(timezone=True), nullable=True)
    slug = Column(Text, unique=True, nullable=False)
