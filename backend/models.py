from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# Clase base de la que heredarán todos nuestros modelos
Base = declarative_base()

class Role(Base):
    """
    Tabla de Roles (Ej: 'Admin', 'Técnico_Redes', 'Integrador_Domótica').
    Crucial para la ciberseguridad: define qué puede hacer y ver cada quien.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200))
    
    # Relación: Un rol puede tener muchos usuarios
    users = relationship("User", back_populates="role")

class User(Base):
    """
    Tabla de Usuarios de Raptor Solutions.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    # NUNCA guardamos la contraseña en texto plano, guardaremos el hash
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    # Llave foránea que conecta al usuario con su nivel de acceso
    role_id = Column(Integer, ForeignKey("roles.id"))
    
    # Relaciones
    role = relationship("Role", back_populates="users")

class Document(Base):
    """
    Tabla de Documentos. Aquí registraremos los manuales técnicos.
    La IA RAG consultará estos registros.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    file_path = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # ¡El control de acceso para la IA!
    # Solo los usuarios con este rol (o superior) podrán usar este documento en el RAG
    required_role_id = Column(Integer, ForeignKey("roles.id"))