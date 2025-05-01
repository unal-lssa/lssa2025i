# Dockerfile para el worker asincrónico basado en hilos

# Imagen base ligera con Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos del componente al contenedor
COPY . .

# Instala Flask para exponer la API REST que recibe tareas
RUN pip install flask

# Ejecuta el servicio worker al iniciar el contenedor
CMD ["python", "app.py"]
