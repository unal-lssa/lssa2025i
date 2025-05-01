# Lab 3 - Secure Microservices Architecture

**Name:** Mario David Montero Galvan
**Document ID** 1065833411

## 🧠 1. Description
Este proyecto implementa una arquitectura de microservicios segura y escalable basada en los principios de **Secure-by-Design**. Utiliza Flask para los servicios, JWT para autenticación, control de acceso por roles, aislamiento por IP, y `Docker Compose` para orquestar todos los componentes. La arquitectura garantiza una superficie de ataque mínima y separación estricta entre servicios.

## 🏗️ 2. Architecture Overview
**Componentes:**
- **API Gateway**: Punto único de entrada, aplica validaciones de IP, JWT y control de rutas.
- **Microservicios**:
  - `auth_service`: autenticación y emisión de tokens JWT.
  - `user_service`: manejo de usuarios.
  - `order_service`: gestión de pedidos (acceso restringido a rol `admin`).
  - `log_service`: servicio interno para guardar eventos.
- **Simulaciones de bases de datos**: cada servicio lee desde su propio archivo local JSON o TXT.

**Flujo:**
Cliente → Load Balancer  → API Gateway → [auth → user | order | log] → Caché  → base de datos simulada

## 🔐 3. Secure-by-Design Tactics
### 🔹 Limit Exposure
- Solo el API Gateway está expuesto públicamente.
- Los microservicios están aislados mediante IP y red interna de Docker.

### 🔹 JWT + Roles
- Emisión de tokens por `auth_service`.
- Rutas protegidas y autorización basada en roles (`user`, `admin`).

### 🔹 Control por IP
- Middleware `limit_exposure`: solo IPs autorizadas acceden a servicios internos.

### 🔹 Logging Interno
- `log_service` solo acepta peticiones desde microservicios, no accesible desde el Gateway.

## 🚀 4. Deployment Instructions

### Requisitos previos
- Docker (v24+)
- Docker Compose (2.0+)

### Ejecución
```bash
git clone git@github.com:unal-lssa/lssa2025i.git
cd lssa2025i
git checkout team3
cd laboratories/laboratory_3/1065833411
docker compose up --build
```

### Verifica contenedores
```bash
docker ps
```

## 🧪 5. Testing Guide

### a. Obtener token JWT
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"username": "user1", "password": "userpass"}' \
     http://localhost:5000/login
```

### b. Acceso sin token (rechazado)
```bash
curl http://localhost:5000/user
```

### c. Acceso directo a microservicio (rechazado por IP)
```bash
curl http://localhost:5001/ -H "Authorization: Bearer <TOKEN>"
```

### d. Acceso válido vía API Gateway
```bash
curl http://localhost:5000/user -H "Authorization: Bearer <TOKEN>"
curl http://localhost:5000/order -H "Authorization: Bearer <TOKEN_ADMIN>"
```

### e. Acceso no autorizado por rol
```bash
curl http://localhost:5000/order -H "Authorization: Bearer <TOKEN_USER>"
```

### f. Simulación de límite de peticiones (agrega rate limiter si lo deseas)
```bash
for i in {1..6}; do
  curl -X POST -H "Content-Type: application/json" \
       -d '{"username": "user1", "password": "userpass"}' \
       http://localhost:5000/login
  echo ""
done
```

---

¡El sistema está diseñado para facilitar extensiones como: trazabilidad, auditoría, métricas o control granular de permisos usando OAuth o servicios de autorización dedicados!
