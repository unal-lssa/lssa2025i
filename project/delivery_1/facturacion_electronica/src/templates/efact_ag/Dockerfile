# Imagen base de Python minimalista
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

COPY . /app

# Instalar dependencias
RUN pip install flask==2.3.2 requests==2.31.0 pyjwt==2.10.1

# Comando para ejecutar la app
CMD ["python", "app.py"]
