from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    ADMIN = "Fundador"
    MODERADOR = "Leader"
    DEVELOPER = "Desenvolvedor"
    MEMBRO = "Auditore"
    PARTNER = "Partner"
    VISITANTE = "Visitante"
