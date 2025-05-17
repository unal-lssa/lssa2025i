Rodriguez Martinez Diego Alejandro
1073252824


# Arquitectura de Microservicios

## Visión General del Sistema

Este sistema implementa una arquitectura de microservicios con los siguientes componentes:

- **API Gateway**: Dirige las solicitudes a los microservicios apropiados
- **Servicio de Caché**: Proporciona funcionalidad de almacenamiento en caché para mejorar el rendimiento
- **Servicio de Base de Datos**: Maneja la persistencia de datos
- **Balanceador de Carga**: Distribuye el tráfico entre los servicios
- **Servicio de Trabajador**: Procesa tareas en segundo plano
- **Microservicio**: Implementación de la lógica de negocio principal

## Actualizaciones Recientes

### Nueva Implementación de Gateway

Se ha añadido un nuevo gateway API alternativo al sistema. El sistema ahora soporta dos implementaciones de gateway:
- Gateway principal (`api_gateway.py`)
- Gateway alternativo (`alternative_api_gateway.py`)

La respuesta ahora incluye información sobre qué gateway procesó la solicitud a través del campo `gateway` en la respuesta. Esto ayuda con la depuración, monitoreo y seguimiento de solicitudes a través del sistema.

### Servicio de Caché Mejorado

El sistema ahora incluye una implementación de caché adicional:
- Caché principal (`cache.py`)
- Caché alternativo (`alternative_cache.py`)

La respuesta incluye información sobre el servicio de caché utilizado a través del campo `service_cache`. Cuando los datos se sirven desde la caché, el campo `cached` será `true`.

## Formato de Respuesta

El sistema ahora devuelve respuestas en el siguiente formato:

```json
{
    "cached": true,
    "data": "Fetched fresh data from DB",
    "gateway": "5000",
    "service_cache": "http://127.0.0.1:5004"
}
```

### Campos de Respuesta:

- `cached`: Booleano que indica si la respuesta fue servida desde la caché
- `data`: Los datos reales que se devuelven
- `gateway`: Identificador del gateway que procesó la solicitud
- `service_cache`: URL o identificador del servicio de caché utilizado (cuando corresponda)

## Arquitectura de Servicios

```
Solicitud del Cliente
    
Balanceador de Carga (load_balancer.py)
    
API Gateway (api_gateway.py o alternative_api_gateway.py)
    
Verificación de Caché (cache.py o alternative_cache.py)
    
Microservicio (microservice.py) → Base de Datos (database.py)
    
Trabajador (worker.py) para tareas en segundo plano
```
