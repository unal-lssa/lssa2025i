# Dockerfile para api_gateway

# Imagen base ligera con Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos del directorio actual al contenedor
COPY . .

# Instala las dependencias necesarias para el API Gateway
RUN pip install flask requests pyjwt

# Comando para ejecutar el servicio API Gateway
CMD ["python", "app.py"]
