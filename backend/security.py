import os
from datetime import datetime, timedelta
from jose import jwt
import bcrypt  # Usamos la librería moderna directamente
from dotenv import load_dotenv

load_dotenv()

# Variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara la contraseña en texto plano con el hash guardado en la base de datos."""
    # bcrypt moderno exige que los textos se conviertan a 'bytes' para procesarlos
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """Recibe una contraseña en texto plano y devuelve el hash seguro."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Lo regresamos a texto normal (string) para que PostgreSQL lo pueda guardar
    return hashed.decode('utf-8')

def create_access_token(data: dict):
    """Fabrica el Token (la pulsera VIP) con los datos del usuario."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt