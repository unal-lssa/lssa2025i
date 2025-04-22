# Imagen base ligera de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos del servicio al contenedor
COPY . .

# Instala Flask y PyJWT
RUN pip install flask pyjwt

# Expone el puerto del servicio para la red interna
EXPOSE 5003

# Comando que lanza el microservicio
CMD ["python", "reporting_service.py"]
