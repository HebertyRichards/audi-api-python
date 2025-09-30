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


class Imagem(Base):
    __tablename__ = "imagens"
    __table_args__ = (
        CheckConstraint(
            "(topic_id IS NOT NULL AND comment_id IS NULL) OR "
            "(topic_id IS NULL AND comment_id IS NOT NULL)",
            name="chk_image_parent",
        ),
        {"schema": "public"},
    )

    id = Column(Integer, primary_key=True)
    url = Column(Text, nullable=False)
    topic_id = Column(
        Integer,
        ForeignKey("public.topicos.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    comment_id = Column(
        Integer,
        ForeignKey("public.comentarios.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("public.profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    uploaded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
