# Imagen base de Python minimalista
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos los archivos al contenedor
COPY . .

# Comando para ejecutar la app
CMD ["python", "app.py"]
