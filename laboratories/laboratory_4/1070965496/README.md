# 🧪 Laboratory 4 - Escalabilidad y Rendimiento

**Nombre completo:** Juan David Ramírez Ávila
**Curso:** Arquitecturas de sofware a gran escala 

---

## 🎯 Objetivo

Este laboratorio muestra cómo mejorar la **escalabilidad** y el **rendimiento** de un sistema distribuido utilizando patrones arquitectónicos clave como:

- **Balanceo de carga**
- **Caché**
- **Procesamiento asíncrono**

---

## 🧱 Componentes del Sistema

### 1. `load_balancer.py`  
Un balanceador de carga simple tipo *round-robin* que distribuye peticiones entre múltiples instancias de un API Gateway.

- Escucha en `http://127.0.0.1:8000`
- Redirige llamadas entrantes a distintas puertas (5000, 5003, 5006)

---

### 2. `api_gateway.py` / `api_gateway_5003.py` / `api_gateway_5006.py`  
Punto de entrada principal del sistema. Realiza:

- Autenticación de token JWT
- Acceso al caché (si existe el dato)
- Acceso al microservicio (si no hay dato en caché)
- Enrutamiento hacia tareas asíncronas

---

### 3. `cache_1.py` y `cache_2.py`  
Dos instancias de un servicio de caché simple en memoria (simulan Redis).

- `cache_1.py`: Puerto 5004  
- `cache_2.py`: Puerto 5007

---

### 4. `database.py`  
Simula una base de datos.  
- Devuelve un mensaje cada vez que se consulta (`/db`)

---

### 5. `microservice.py`  
Representa un servicio con lógica de negocio sincrónica.  
- Endpoints simples como `/process`

---

### 6. `worker.py`  
Servicio que procesa tareas largas en segundo plano.  
- Usa hilos (threads) para simular ejecución asincrónica

---

### 7. `load_tester.py`  
Script que envía múltiples peticiones concurrentes al sistema para probar el balanceo de carga y el comportamiento del caché.

- Envia 50 peticiones al endpoint `/data`
- Usa un token JWT válido

---

## 🔄 Flujo de Datos (Simplificado)

```
Cliente (curl o script) 
      ↓
Load Balancer (8000)
      ↓
API Gateway (5000 / 5003 / 5006)
      ↓
Cache (5004 / 5007) ←→ Base de Datos (5002)
```

Para tareas largas:

```
Cliente
  ↓
API Gateway → Worker (5005)
```

---

## 🛠️ Cómo Ejecutar el Proyecto

Abre una terminal por cada servicio y ejecuta:

```bash
python cache_1.py
python cache_2.py
python database.py
python microservice.py
python worker.py
python api_gateway.py
python api_gateway_5003.py
python api_gateway_5006.py
python load_balancer.py
```

### Probar Endpoints Manualmente

```bash
# Token JWT válido
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidGVzdF91c2VyIn0.NiAjMp8K9re-WJE_BJbqCmLBF4yFr0rDZwNRHj9Cbb8"

# Obtener datos
curl -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidGVzdF91c2VyIn0.NiAjMp8K9re-WJE_BJbqCmLBF4yFr0rDZwNRHj9Cbb8" http://127.0.0.1:8000/data

# Ejecutar tarea asíncrona
curl -X POST -H "Content-Type: application/json" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidGVzdF91c2VyIn0.NiAjMp8K9re-WJE_BJbqCmLBF4yFr0rDZwNRHj9Cbb8" -d '{"task":"report"}' http://127.0.0.1:8000/longtask
```

### Probar con carga automatizada

```bash
python load_tester.py
```

---

## 🔧 Mejoras Realizadas

Esta versión incluye **mejoras importantes** respecto a la arquitectura inicial del laboratorio:

✅ **Balanceo de carga con más instancias:**  
Se agregaron 3 instancias del API Gateway (puertos 5000, 5003 y 5006) y un balanceador tipo round-robin que distribuye el tráfico.

✅ **Caché distribuido simulado:**  
Ahora hay 2 servicios de caché independientes, y el API Gateway elige aleatoriamente uno por cada solicitud.

✅ **Script de prueba de carga:**  
Se incluyó un script que genera múltiples peticiones concurrentes para observar el comportamiento real del balanceo y caché.

✅ **Separación clara de responsabilidades:**  
Cada componente tiene una función clara, lo que permite escalar horizontalmente con facilidad.

✅ **Autenticación integrada (JWT):**  
Se mantiene la seguridad de las peticiones mediante tokens válidos.

---

## 📌 Recomendaciones

- Para una solución en producción, reemplazar el caché en memoria por **Redis**.
- Usar herramientas como **Nginx** para balanceo real.
- Implementar un sistema de colas real como **RabbitMQ** para tareas asíncronas.

---

Este laboratorio muestra cómo una arquitectura segmentada puede responder eficientemente a altos volúmenes de usuarios y datos
