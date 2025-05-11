# Laboratorio 4
**Yilver Ramírez Ochoa – C.C. 1015994056**

---

## Objetivo

Demostrar cómo la aplicación de tácticas de rendimiento y escalabilidad, utilizando patrones arquitectónicos como balanceo de carga (Load Balancing) y almacenamiento en caché (Caching), puede mejorar la capacidad de respuesta del sistema y permitir soportar mayores cargas.

---

## 🔧 Instrucciones de ejecución

### 1. Ejecutar todos los servicios (cada uno en una terminal diferente)

```bash
python cache.py
python database.py
python microservice.py
python microservice_heavy.py
python worker.py
python api_gateway.py         # puerto 5000
python api_gateway5003.py     # puerto 5003
python load_balancer.py       # puerto 8000
```

---

### 2. Probar balanceo de carga y caché

Utilizar `curl.exe` con un token válido:

```bash
curl.exe -L -X GET http://127.0.0.1:8000/data -H "X-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIxIn0.xMpiGanjLuT9-P3BXbsI6pKa8BB2suAXkxltSwrGFOc"
```

Resultados esperados:
- Primer acceso:
  ```json
  { "cached": false, "data": "Fetched fresh data from DB" }
  ```
- Segundo acceso:
  ```json
  { "cached": true, "data": "Fetched fresh data from DB" }
  ```

Para observar el balanceo, ejecutar sin `-L`:

```bash
curl.exe -X GET http://127.0.0.1:8000/data -H "X-Token: eyJ..."
```

Esto permitirá ver redirecciones a:
- `http://127.0.0.1:5000/data`
- `http://127.0.0.1:5003/data`

---

### 3. Lanzar tarea asíncrona

```bash
curl.exe -L -X POST http://127.0.0.1:8000/longtask -H "Content-Type: application/json" -H "X-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIxIn0.xMpiGanjLuT9-P3BXbsI6pKa8BB2suAXkxltSwrGFOc" -d "{"task": "report"}"
```

Respuesta esperada:
```json
{ "status": "Task queued" }
```

En la terminal del worker debería aparecer:
```
Processing task: {'task': 'report'}
Task complete
```

---

### 4. [Mejora] Microservicio adicional para carga pesada

Se añadió `microservice_heavy.py`, que simula una operación más costosa al exponer el endpoint `/process-heavy`.

Probar con:

```bash
curl.exe -L -X GET http://127.0.0.1:8000/process-heavy -H "X-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIxIn0.xMpiGanjLuT9-P3BXbsI6pKa8BB2suAXkxltSwrGFOc"
```

Resultado esperado:
```json
{
  "origin": "gateway 500X",
  "data": { "message": "Heavy process executed" }
}
```

Esta mejora demuestra escalabilidad horizontal al redirigir procesos costosos a un microservicio especializado.

---

## Conclusión

Al aplicar tácticas de rendimiento y escalabilidad a la arquitectura original:

- Se introdujo **balanceo de carga** para distribuir el tráfico.
- Se redujo la latencia mediante el uso de **caché**.
- Se descargaron procesos lentos con **procesamiento asíncrono**.
- Se añadió un **microservicio especializado** para demostrar escalabilidad horizontal.

Este diseño simula cómo los sistemas reales mantienen la capacidad de respuesta bajo una demanda creciente.

---

## Contenido de la carpeta

```
├── api_gateway.py
├── api_gateway5003.py
├── cache.py
├── database.py
├── microservice.py
├── microservice_heavy.py
├── worker.py
├── load_balancer.py
├── generar_token.py
├── README.md
├── Evidencias.pdf
```

---

## Autor

**Yilver Ramírez Ochoa**  
**C.C. 1015994056**  
**Universidad Nacional de Colombia – LSSA 2025-I**
