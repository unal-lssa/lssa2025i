# Imagen base minimalista de Python
FROM python:3.11-slim

# Directorio de trabajo del contenedor
WORKDIR /app

# Copiar el código fuente al contenedor
COPY . .

# Instalar dependencias requeridas
RUN pip install flask pyjwt

# Exponer el puerto 5002 usado por este servicio
EXPOSE 5002

# Comando para iniciar el servicio
CMD ["python", "inventory_service.py"]
