import uuid
import enum
from sqlalchemy import (
    Column, String, Text, Date, DateTime, Integer,
    ForeignKey, CheckConstraint, UniqueConstraint 
)
from sqlalchemy.dialects.postgresql import UUID, ENUM as SQLAlchemyEnum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = 'Fundador'
    MODERADOR = 'Leader'
    DEVELOPER = 'Desenvolvedor'
    MEMBRO = 'Auditore'
    PARTNER = 'Partner'
    VISITANTE = 'Visitante'

class Profile(Base):
    __tablename__ = 'profiles'
    __table_args__ = {'schema': 'public'}
    id = Column(UUID(as_uuid=True), 
                ForeignKey('auth.users.id', ondelete='CASCADE'), 
                primary_key=True, 
                default=uuid.uuid4)
                
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

class Follower(Base):
    __tablename__ = 'followers'
    __table_args__ = (
        CheckConstraint('follower_id <> following_id', name='check_not_following_self'),
        {'schema': 'public'}
    )
    follower_id = Column(UUID(as_uuid=True),
                         ForeignKey('public.profiles.id', ondelete='CASCADE'),
                         primary_key=True)
    following_id = Column(UUID(as_uuid=True),
                          ForeignKey('public.profiles.id', ondelete='CASCADE'),
                          primary_key=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(),
                        nullable=False)

class OnlineUser(Base):
    __tablename__ = 'online_users'
    __table_args__ = {'schema': 'public'}
    user_id = Column(UUID(as_uuid=True),
                     ForeignKey('public.profiles.id', ondelete='CASCADE'),
                     primary_key=True)
    last_seen_at = Column(DateTime(timezone=True),
                          server_default=func.now(),
                          nullable=False)

class Categoria(Base):
    __tablename__ = 'categorias'
    __table_args__ = {'schema': 'public'}
    slug = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)

class CategoryTopicPermission(Base):
    __tablename__ = 'category_topic_permissions'
    __table_args__ = (
        UniqueConstraint('category_slug', 'user_role', name='unique_permission_topic'),
        {'schema': 'public'}
    )
    id = Column(Integer, primary_key=True)
    category_slug = Column(Text,
                           ForeignKey('public.categorias.slug', ondelete='CASCADE'),
                           nullable=False)
    user_role = Column(SQLAlchemyEnum(UserRole, name='user_role', create_type=False),
                       nullable=False)

class CategoryCommentPermission(Base):
    __tablename__ = 'category_comment_permissions'
    __table_args__ = (
        UniqueConstraint('category_slug', 'user_role', name='unique_permission_comment'),
        {'schema': 'public'}
    )
    id = Column(Integer, primary_key=True)
    category_slug = Column(Text,
                           ForeignKey('public.categorias.slug', ondelete='CASCADE'),
                           nullable=False)
    user_role = Column(SQLAlchemyEnum(UserRole, name='user_role', create_type=False),
                       nullable=False)
    
class Topico(Base):
    __tablename__ = 'topicos'
    __table_args__ = (
        CheckConstraint('length(content) <= 2000', name='content_length_check'),
        {'schema': 'public'}
    )
    
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    author_id = Column(UUID(as_uuid=True), 
                       ForeignKey('public.profiles.id', ondelete='CASCADE'), 
                       nullable=False)
    category = Column(Text, 
                      ForeignKey('public.categorias.slug', ondelete='RESTRICT'), 
                      nullable=False)
    created_in = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_in = Column(DateTime(timezone=True), nullable=True)
    slug = Column(Text, unique=True, nullable=False)


class Comentario(Base):
    __tablename__ = 'comentarios'
    __table_args__ = (
        CheckConstraint('length(content) <= 2000', name='content_length_check'),
        {'schema': 'public'}
    )

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), 
                       ForeignKey('public.profiles.id', ondelete='CASCADE'), 
                       nullable=False)
    topic_id = Column(Integer, 
                      ForeignKey('public.topicos.id', ondelete='CASCADE'), 
                      nullable=False)
    created_in = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_in = Column(DateTime(timezone=True), nullable=True)


class Imagem(Base):
    __tablename__ = 'imagens'
    __table_args__ = (
        CheckConstraint(
            '(topic_id IS NOT NULL AND comment_id IS NULL) OR '
            '(topic_id IS NULL AND comment_id IS NOT NULL)',
            name='chk_image_parent'
        ),
        {'schema': 'public'}
    )

    id = Column(Integer, primary_key=True)
    url = Column(Text, nullable=False)
    topic_id = Column(Integer, 
                      ForeignKey('public.topicos.id', ondelete='CASCADE'), 
                      index=True, 
                      nullable=True)
    comment_id = Column(Integer, 
                        ForeignKey('public.comentarios.id', ondelete='CASCADE'), 
                        index=True, 
                        nullable=True)
    author_id = Column(UUID(as_uuid=True), 
                       ForeignKey('public.profiles.id', ondelete='CASCADE'), 
                       nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)