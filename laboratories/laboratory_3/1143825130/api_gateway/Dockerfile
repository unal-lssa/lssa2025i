# Imagen base de Python minimalista
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar todos los archivos al contenedor
COPY . .

# Instalación de dependencias necesarias
RUN pip install flask pyjwt requests

# Puerto expuesto
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python", "api_gateway.py"]
