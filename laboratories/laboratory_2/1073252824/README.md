Rodriguez Martinez Diego Alejandro
1073252824

# Sistema con Balanceador de Carga

 Se agrega un balanceador de carga (NGINX). El objetivo es distribuir las peticiones del frontend hacia uno o varios backends a través del balanceador.

## 🔧 Cómo validar que el balanceador funciona

El balanceador NGINX ha sido configurado para registrar en su log cada petición que pasa por él y a qué backend fue redirigida. Puedes usar el siguiente comando para monitorear estos registros directamente:

```bash
docker-compose logs -f lssa_lb
