# Dockerfile para el servicio parallel_worker (procesamiento en paralelo)

# Imagen base mínima con Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos fuente al contenedor
COPY . .

# Instala Flask para exponer la API REST del servicio
RUN pip install flask

# Comando para ejecutar el servicio de tareas paralelas
CMD ["python", "app.py"]
