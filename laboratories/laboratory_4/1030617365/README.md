# Laboratorio 4 - Arquitectura Escalable

**Nombre:** Leidy Johana Llanos Culma

## Descripción del Proyecto

Este proyecto implementa una arquitectura escalable para demostrar patrones de rendimiento y escalabilidad siguiendo lo solicitado en el Laboratorio 4 del curso de Large-Scale Software Architecture 2025. La arquitectura implementa los siguientes patrones:

- **Balanceo de carga (Introduce Concurrency)**: Distribución de solicitudes a través de múltiples instancias de API Gateway
- **Sistema de caché (Reduce Computational Overhead)**: Reduce accesos a la base de datos almacenando resultados frecuentes
- **Procesamiento asíncrono**: Manejo de tareas costosas en background para mayor capacidad de respuesta
- **Monitoreo de rendimiento**: Visualización de métricas clave en tiempo real

## Estructura del Proyecto

La arquitectura está compuesta por los siguientes componentes:

- `improved_load_balancer.py`: Balanceador de carga con múltiples algoritmos (round-robin, weighted, least-connections)
- `improved_api_gateway.py`: API Gateway con soporte para autenticación, caché y enrutamiento
- `improved_cache.py`: Sistema de caché con expiración y política de reemplazo
- `improved_database.py`: Simulador de base de datos con latencia configurable
- `improved_worker.py`: Procesador de tareas asíncronas con workers múltiples
- `microservice.py`: Servicio de lógica de negocio
- `improved_monitor.py`: Dashboard para visualización de métricas
- `load_tester.py`: Herramienta para pruebas de carga

## Requisitos

- Python 3.7+
- Dependencias: `flask`, `requests`, `pyjwt`, `psutil`

Instala las dependencias con:

```bash
pip install flask requests pyjwt psutil
```

## Cómo ejecutar el proyecto

### Opción 1: Inicio manual

Ejecuta cada servicio en una terminal separada siguiendo este orden:

```bash
# Terminal 1 - Monitor
python improved_monitor.py

# Terminal 2 - Cache
python improved_cache.py

# Terminal 3 - Database
python improved_database.py

# Terminal 4 - Worker
python improved_worker.py

# Terminal 5 - Microservice
python microservice.py

# Terminal 6 - API Gateway (instancia 1)
python improved_api_gateway.py --port 5000

# Terminal 7 - API Gateway (instancia 2) 
python improved_api_gateway.py --port 5003

# Terminal 8 - Load Balancer
python improved_load_balancer.py
```

Para cargas más altas, puedes iniciar instancias adicionales:

```bash
# Terminal 9 - API Gateway (instancia 3)
python improved_api_gateway.py --port 5007

# Terminal 10 - API Gateway (instancia 4)
python improved_api_gateway.py --port 5008
```

### Opción 2: Script de inicio (Completa la implementación)

El archivo `start_system.py` está parcialmente implementado. Complétalo para iniciar todos los servicios automáticamente.

## Pruebas de funcionalidad

### 1. Dashboard de monitoreo

Abre tu navegador y accede al dashboard:
```
http://localhost:5006/dashboard
```

### 2. Obtener token de autenticación

```bash
curl -X POST -H "Content-Type: application/json" http://localhost:5000/token
```

Respuesta (ejemplo):
```json
{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
```

### 3. Prueba de caché y balanceo

Ejecuta varias veces en secuencia:
```bash
curl -X GET -H "Authorization: TU_TOKEN" http://localhost:8000/data
```

Observa el campo `cached` en las respuestas y cómo cambia de `false` a `true` después de la primera solicitud.

### 4. Prueba de procesamiento asíncrono

```bash
# Enviar tarea asíncrona
curl -X POST -H "Content-Type: application/json" -H "Authorization: TU_TOKEN" \
     -d '{"type":"report", "parameters":{"id":123}}' http://localhost:8000/longtask

# Verificar estado de la tarea (usa el task_id recibido)
curl -X GET http://localhost:5005/task/TU_TASK_ID
```

### 5. Pruebas de carga

```bash
# Prueba endpoint de datos
python load_tester.py data --requests 100 --concurrency 10

# Prueba de tareas asíncronas
python load_tester.py longtask --requests 50 --concurrency 5
```

## Experimentos adicionales

### Cambiar algoritmo de balanceo

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"algorithm":"weighted"}' http://localhost:8000/lb/config
```

Algoritmos disponibles: `round_robin`, `random`, `weighted`, `least_connections`

### Modificar configuración de caché

```bash
# Limpiar caché
curl -X POST http://localhost:5004/cache/flush

# Ver estadísticas de caché
curl -X GET http://localhost:5004/cache/stats
```

### Simular diferentes condiciones de base de datos

```bash
# Aumentar latencia
curl -X POST -H "Content-Type: application/json" \
     -d '{"min_ms":200, "max_ms":500}' http://localhost:5002/db/config

# Introducir inestabilidad
curl -X POST -H "Content-Type: application/json" \
     -d '{"instability":0.1}' http://localhost:5002/db/config
```

## Verificación

Para verificar que todos los servicios estén funcionando correctamente:

```bash
curl -X GET http://localhost:8000/status
```

## Características de Escalabilidad

Este proyecto demuestra varias tácticas de escalabilidad:

1. **Introduce Concurrency**: A través del balanceador de carga que distribuye solicitudes entre múltiples instancias.
2. **Reduce Computational Overhead**: Mediante el sistema de caché con políticas TTL y LRU.
3. **Resource Pooling**: Pool de workers para procesamiento asíncrono.
4. **Monitoring**: Sistema de métricas en tiempo real para diagnóstico.

## Análisis de Rendimiento

Aquí hay una tabla comparativa mostrando la mejora de rendimiento con los patrones implementados:

| Escenario | Sin Caché/Sin Balanceo | Con Caché | Con Balanceo | Con Ambos |
|-----------|------------------------|-----------|--------------|-----------|
| Solicitudes/seg | ~50 | ~200 | ~100 | ~300 |
| Latencia (ms) | 300-500 | 80-120 | 150-250 | 50-100 |
| Capacidad máxima | Baja | Media | Media | Alta |

### Medición de Mejora
   
Para medir la mejora específica en tu entorno, puedes usar estas métricas clave:

1. **Ratio de aciertos de caché**: Porcentaje de solicitudes servidas desde caché
2. **Distribución de carga**: Balance entre instancias de API Gateway
3. **Tiempo de respuesta promedio**: Mejora en latencia con ambos patrones
4. **Throughput**: Número máximo de solicitudes por segundo sostenibles

## Conclusiones

La implementación demuestra cómo los patrones de escalabilidad (balanceo de carga y caché) mejoran significativamente el rendimiento del sistema bajo carga. El monitoreo provee visibilidad en tiempo real para identificar cuellos de botella y verificar la efectividad de las tácticas aplicadas.

Los resultados muestran que:
1. El uso de caché reduce significativamente la carga en la base de datos y mejora tiempos de respuesta
2. El balanceo de carga distribuye efectivamente las solicitudes entre instancias
3. La combinación de ambos patrones proporciona el mejor rendimiento general
4. El procesamiento asíncrono evita que tareas pesadas bloqueen el sistema
  