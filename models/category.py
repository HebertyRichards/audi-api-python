from sqlalchemy import Column, Text
from .base import Base


class Categoria(Base):
    __tablename__ = "categorias"
    __table_args__ = {"schema": "public"}
    slug = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
