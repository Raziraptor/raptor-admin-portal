from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, security
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import models, schemas, security
from database import engine, SessionLocal
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import shutil
import os
import models, schemas, security, ai_core
from database import engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from security import get_password_hash

# Crea las tablas si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Raptor Solutions Admin API",
    description="API para gestión administrativa segura y Asistente RAG"   
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción aquí va la URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_seed_data():
    db = SessionLocal()
    try:
        # 1. PRIMERO: Asegurarnos de que el Rol 1 exista
        # (Ajusta 'name' u otras columnas según cómo definiste tu clase Role en models.py)
        admin_role = db.query(models.Role).filter(models.Role.id == 1).first()
        if not admin_role:
            print("🌱 Sembrando Rol de Administrador...")
            new_role = models.Role(id=1, name="Administrador") # Ajusta los campos si es necesario
            db.add(new_role)
            db.commit() # Guardamos el rol antes de continuar
            
        # 2. SEGUNDO: Crear el usuario ahora que el rol ya existe
        admin = db.query(models.User).filter(models.User.email == "admin@raptorsolutions.com").first()
        if not admin:
            print("🌱 Sembrando Usuario Administrador...")
            hashed_password = get_password_hash("RaptorAdmin2026!") 
            new_admin = models.User(
                email="admin@raptorsolutions.com", 
                hashed_password=hashed_password,
                role_id=1 # ¡Ahora sí existe el rol 1!
            )
            db.add(new_admin)
            db.commit()
            print("✅ Datos semilla instalados con éxito.")
        else:
            print("✅ Los datos semilla ya estaban instalados.")
    finally:
        db.close()

create_seed_data()

# --- INYECCIÓN DE DEPENDENCIAS ---
# Esta función abre una sesión con PostgreSQL cada vez que un usuario hace una 
# petición y la cierra automáticamente al terminar. Previene fugas de memoria.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Esta función intercepta la petición, lee el token y devuelve al usuario."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Intentamos abrir el candado del token con nuestra llave secreta
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        
        # 2. Extraemos el correo que guardamos adentro
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except JWTError:
        # Si el token es falso o ya expiró, lo rechazamos
        raise credentials_exception
        
    # 3. Buscamos al usuario en la base de datos para confirmar que sigue activo
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user

@app.get("/")
def read_root():
    return {"status": "online", "mensaje": "Sistemas de Raptor Solutions nominales."}

# --- ENDPOINTS DE ROLES ---
# Nota: usamos response_model=schemas.RoleResponse para filtrar los datos de salida
@app.post("/roles/", response_model=schemas.RoleResponse)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    # 1. Verificamos si el rol ya existe para no duplicarlo
    db_role = db.query(models.Role).filter(models.Role.name == role.name).first()
    if db_role:
        raise HTTPException(status_code=400, detail="Este rol ya existe.")
    
    # 2. Convertimos el schema (Pydantic) a un modelo de base de datos (SQLAlchemy)
    new_role = models.Role(name=role.name, description=role.description)
    
    # 3. Guardamos en PostgreSQL
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

# --- ENDPOINTS DE USUARIOS ---
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Verificamos que el correo no esté en uso
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")
    
    # 2. CIBERSEGURIDAD: Hasheamos la contraseña antes de crear el objeto
    hashed_pwd = security.get_password_hash(user.password)
    
    # 3. Creamos el modelo (sin guardar la contraseña en texto plano)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pwd,
        full_name=user.full_name,
        role_id=user.role_id
    )
    
    # 4. Guardamos en PostgreSQL
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # FastAPI usará UserResponse automáticamente para NO devolver la contraseña en la respuesta final
    return new_user

# --- ENDPOINT DE LOGIN ---
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Buscar al usuario (Nota: OAuth2 usa el campo 'username' por defecto, ahí enviaremos el correo)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # 2. Verificar que exista y la contraseña coincida
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Si todo está bien, fabricamos el token. 
    # Ciberseguridad: Guardamos dentro del token su correo y su ROL.
    access_token = security.create_access_token(
        data={"sub": user.email, "role_id": user.role_id}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# --- ZONA PROTEGIDA ---
@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Este endpoint está bloqueado. Si llegas aquí, el guardia (get_current_user)
    ya validó tu token y sabe quién eres. Simplemente devolvemos tus datos.
    """
    return current_user

# --- ENDPOINTS DE INTELIGENCIA ARTIFICIAL (RAG) ---

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    required_role_id: int = Form(...),
    current_user: models.User = Depends(get_current_user)
):
    """Sube un PDF y lo convierte en vectores para la IA."""
    
    # CIBERSEGURIDAD: Solo un Administrador (supongamos que el ID 1 es Admin) puede subir documentos
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Privilegios insuficientes para subir manuales.")
        
    # Guardamos el archivo físicamente en la carpeta
    file_path = f"uploaded_docs/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Llamamos a nuestro motor de IA para que lea, divida y guarde en ChromaDB
    chunks_procesados = ai_core.process_and_store_document(file_path, required_role_id)
    
    return {
        "mensaje": f"Documento '{file.filename}' ingerido correctamente por la IA.",
        "fragmentos_vectorizados": chunks_procesados,
        "nivel_de_seguridad_asignado": required_role_id
    }

@app.get("/documents")
def list_documents(current_user = Depends(get_current_user)):
    docs = ai_core.get_uploaded_documents()
    return {"documents": docs}

@app.delete("/documents/{filename}")
def delete_doc(filename: str, current_user = Depends(get_current_user)):
    deleted_count = ai_core.delete_document(filename)
    if deleted_count == 0:
        return {"message": f"Documento '{filename}' no encontrado."}
    return {"message": f"Documento '{filename}' eliminado. ({deleted_count} fragmentos borrados)"}

@app.post("/chat")
def chat_with_assistant(
    chat_request: schemas.ChatRequest,
    current_user: models.User = Depends(get_current_user)
):
    """Chatea con la IA. La IA responderá según el Nivel de Acceso del usuario."""
    
    # Le pasamos la pregunta y EL ROL EXACTO del usuario a LangChain
    respuesta = ai_core.ask_assistant(chat_request.question, current_user.role_id)
    
    return {"respuesta": respuesta}