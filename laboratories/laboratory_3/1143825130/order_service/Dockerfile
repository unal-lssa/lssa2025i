# Imagen base liviana de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copiar el contenido del servicio
COPY . .

# Instalación de Flask y PyJWT
RUN pip install flask pyjwt

# Exponer el puerto para conexión dentro de la red interna
EXPOSE 5001

# Comando de arranque
CMD ["python", "order_service.py"]
