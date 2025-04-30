# Dockerfile para el servicio de cache

# Usa una imagen ligera con Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos locales al directorio de trabajo del contenedor
COPY . .

# Instala Flask para el microservicio HTTP
RUN pip install flask

# Ejecuta el servicio de caché
CMD ["python", "app.py"]
