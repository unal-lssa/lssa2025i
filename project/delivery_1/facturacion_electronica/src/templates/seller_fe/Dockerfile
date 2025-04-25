# Imagen base oficial de Node.js
FROM node:18-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY . .

# Instalar dependencias
RUN npm install

# Comando para arrancar la app
CMD ["node", "app.js"]
