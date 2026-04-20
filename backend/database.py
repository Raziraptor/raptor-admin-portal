import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()

# 1. EL FALLBACK INFALIBLE: 
# Si Docker falla y devuelve None, Python inyectará esta ruta automáticamente.
URL_POR_DEFECTO = "postgresql://postgres:Raee.2853083@db:5432/raptor_db"
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", URL_POR_DEFECTO)

# Creamos el "motor". Este es el objeto que maneja la conexión real con PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

if not SQLALCHEMY_DATABASE_URL or "sqlite" in SQLALCHEMY_DATABASE_URL:
    raise ValueError("¡ALERTA! El backend no está leyendo el .env de Postgres.")

# Creamos la fábrica de sesiones (cada vez que un usuario hace una petición, abrimos una sesión)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)