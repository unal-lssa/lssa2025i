# Usa la imagen oficial de MySQL como base
FROM mysql:8

# Copia el archivo init.sql al directorio de inicialización de MySQL
COPY ./init.sql /docker-entrypoint-initdb.d/init.sql
