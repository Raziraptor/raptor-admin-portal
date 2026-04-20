from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    question: str

# --- SCHEMAS PARA ROLES ---
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass # Usamos esto cuando el usuario crea un rol (no le pedimos ID)

class RoleResponse(RoleBase):
    id: int
    
    class Config:
        from_attributes = True # Esto le dice a Pydantic que lea datos de SQLAlchemy

# --- SCHEMAS PARA USUARIOS ---
class UserBase(BaseModel):
    email: EmailStr # Valida automáticamente que sea un formato de correo real
    full_name: Optional[str] = None
    role_id: int

class UserCreate(UserBase):
    password: str = Field(max_length=72) # Cuando creamos el usuario, pedimos la contraseña en texto plano

class UserResponse(UserBase):
    id: int
    is_active: bool
    # Nota de Ciberseguridad: ¡NUNCA devolvemos la contraseña en el Response!

    class Config:
        from_attributes = True