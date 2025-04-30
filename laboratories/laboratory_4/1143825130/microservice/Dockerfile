# Dockerfile para el microservicio funcional

# Imagen base ligera de Python 3.10
FROM python:3.10-slim

# Establece el directorio donde se ejecutará la app
WORKDIR /app

# Copia los archivos de la carpeta actual al contenedor
COPY . .

# Instala únicamente Flask, necesario para la API REST del microservicio
RUN pip install flask

# Ejecuta el microservicio
CMD ["python", "app.py"]
