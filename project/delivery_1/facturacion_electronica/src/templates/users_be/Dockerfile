# Imagen base oficial de Python
FROM python:3.11-slim

# Establecer directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias
RUN pip install --no-cache-dir flask==2.3.2 mysql-connector-python==9.3.0

# Copiar el código fuente de la app
COPY . /app

# Comando para ejecutar la app
CMD ["python", "app.py"]
