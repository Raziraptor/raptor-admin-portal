# Usamos una versión ligera y moderna de Python
FROM python:3.12-slim

# Le decimos a Docker dónde trabajar adentro del contenedor
WORKDIR /app

# Copiamos la lista de dependencias y las instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código fuente de tu backend
COPY . .

# Exponemos el puerto de FastAPI
EXPOSE 8000

# El comando que arranca el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]