# Dockerfile para el servicio simulado de base de datos

# Imagen base ligera de Python 3.10
FROM python:3.10-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos del directorio local al contenedor
COPY . .

# Instalación de Flask para exponer la API REST simulada
RUN pip install flask

# Comando que inicia el servicio
CMD ["python", "app.py"]
