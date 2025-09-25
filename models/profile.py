import uuid
from sqlalchemy import (Column, String, Text, Date, DateTime, Integer, Enum as SQLAlchemyEnum, ForeignKey)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class UserRole(SQLAlchemyEnum):
    ADMIN = 'Fundador'
    MODERADOR = 'Leader'
    DEVELOPER = 'Desenvolvedor'
    MEMBRO = 'Auditore'
    PARTNER = 'Partner'
    VISITANTE = 'Visitante'

class Profile(Base):
    __tablename__ = 'profiles'
    __table_args__ = {'schema': 'public'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, 
                foreign_key=ForeignKey('auth.users.id', ondelete='CASCADE'))
    username = Column(String, unique=True, nullable=False)
    website = Column(Text, nullable=True)
    gender = Column(Text, nullable=True)
    birthdate = Column(Date, nullable=True)
    location = Column(Text, nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    role = Column(SQLAlchemyEnum(UserRole, name='user_role', create_type=False), 
                  nullable=False, default=UserRole.VISITANTE)
    facebook = Column(Text, nullable=True)
    instagram = Column(Text, nullable=True)
    discord = Column(Text, nullable=True)
    steam = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)
    followers_count = Column(Integer, nullable=False, default=0)
    following_count = Column(Integer, nullable=False, default=0)
    mensagens_count = Column(Integer, nullable=False, default=0)