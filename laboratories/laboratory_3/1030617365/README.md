# Laboratorio 3 - Seguridad: Sistema de Microservicios con API Gateway Mejorado

### Nombre: Leidy Johana Llanos Culma 
### Documento: 1030617365

## Descripción del Proyecto
Este proyecto implementa una arquitectura de microservicios que demuestra la importancia de la táctica de seguridad "Limit Exposure" (Limitar Exposición) utilizando un patrón de API Gateway como punto de acceso centralizado.

El proyecto original ha sido mejorado con:

Servicios adicionales: Se agregaron User Service, Order Service, Product Service
Reglas más complejas de limitación de exposición:
Control de acceso basado en roles (RBAC)
Restricción por IP basada en roles
Límite de tasa de peticiones (Rate Limiting)
Tokens JWT con expiración
Registro de auditoría (Logging)
Mayor seguridad: Centralización de autenticación y autorización en el API Gateway
Arquitectura del Sistema
Cliente → API Gateway (expuesto) → Microservicios (protegidos) → Base de Datos (protegida)
#### Los componentes incluyen:

**API Gateway:** El único punto de entrada, implementa autenticación, autorización y límites de exposición
**User Service:** Gestiona datos de usuarios
**Order Service:** Gestiona pedidos
**Product Service:** Gestiona productos
**Database Service:** Simula operaciones de base de datos (acceso muy restringido)
**Táctica de Seguridad:** Limit Exposure

La implementación mejorada aplica la táctica "Limit Exposure" mediante:

**IP Whitelisting:** Solo IPs específicas pueden acceder a servicios, con acceso diferenciado por rol
**Autenticación JWT:** Se requieren tokens válidos firmados para todas las operaciones protegidas
**Control de Acceso por Roles:** Los roles de usuario determinan qué servicios pueden usar
**Límite de Frecuencia de Peticiones:** Previene ataques de fuerza bruta y DDoS
**Logging Detallado:** Registro completo de accesos e intentos fallidos para auditoría

#### Requisitos
Python 3.x
Flask (pip install flask)
PyJWT (pip install pyjwt)

#### Instrucciones de Ejecución

Opción 1: Ejecución centralizada 
bash
python run_secure_system.py

Opción 2: Ejecución manual
Ejecute cada servicio en una terminal distinta:

bash
### Terminal 1 - API Gateway
python api_gateway_enhanced.py

### Terminal 2 - User Service
python user_service.py

### Terminal 3 - Order Service
python order_service.py

### Terminal 4 - Product Service
python product_service.py


### Terminal 6 - Database Service
python database_service.py

## Prueba del Sistema
1. Obtener un token JWT (login)
Usuario normal:
bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "user1", "password": "password123"}' http://localhost:5000/login
Administrador:
bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin1", "password": "admin123"}' http://localhost:5000/login
Analista:
bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "analyst1", "password": "analyst123"}' http://localhost:5000/login
2. Acceder a los servicios con el token
bash
# Reemplazar YOUR_TOKEN_HERE con el token JWT recibido
curl -X GET -H "Authorization: YOUR_TOKEN_HERE" http://localhost:5000/user
curl -X GET -H "Authorization: YOUR_TOKEN_HERE" http://localhost:5000/order
curl -X GET -H "Authorization: YOUR_TOKEN_HERE" http://localhost:5000/product

# Solo para rol analista
curl -X GET -H "Authorization: ANALYST_TOKEN_HERE" http://localhost:5000/analytics

# Solo para rol administrador
curl -X GET -H "Authorization: ADMIN_TOKEN_HERE" http://localhost:5000/db
Explicación de Mejoras
