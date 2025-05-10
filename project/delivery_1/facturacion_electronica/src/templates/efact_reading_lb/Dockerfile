# Imagen base de NGINX
FROM nginx:1.25-alpine

# Eliminar configuración por defecto y añadir la personalizada
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf
