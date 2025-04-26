# Laboratorio 3 - Seguridad: Sistema de Microservicios con API Gateway

### Nombre: Leidy Johana Llanos Culma 
### Documento: 1030617365

## Descripción del Proyecto
Este proyecto implementa un API Gateway de microservicios con múltiples capas de seguridad, incluyendo autenticación con JWT, control de acceso basado en roles (RBAC), restricciones de IP y límites de tasa de solicitudes.

## Características

- **Autenticación JWT**: Sistema de tokens seguro con expiración
- **Control de Acceso Basado en Roles (RBAC)**: Diferentes niveles de acceso según el rol del usuario
- **Lista Blanca de IPs**: Restricción de acceso por dirección IP
- **Límite de Tasa de Solicitudes**: Protección contra abusos limitando el número de solicitudes por hora
- **Registro (Logging)**: Registro detallado de actividades y eventos de seguridad
- **Enrutamiento de Servicios**: Redirección transparente a los microservicios correspondientes

## Requisitos

- Python 3.x
- Flask (pip install flask)
- PyJWT (pip install pyjwt)
- Requests

#### Instrucciones de Ejecución

1. Inicia el API Gateway:
   ```bash
   python api_gateway.py
   ```
   python user_service.py
   ```
   python product_service.py
   ```
   python order_service.py

2. El servidor se iniciará en `http://0.0.0.0:5000`

## Estructura del Sistema

El API Gateway actúa como punto de entrada centralizado para todos los microservicios:

```
Cliente -> API Gateway -> Microservicios (user_service, order_service, product_service, etc.)
```

## Consumir los Servicios

### 1. Obtener un Token JWT (Login)

```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'
```

Respuesta exitosa:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. Acceder a los Servicios con el Token

Servicio de Usuarios:
```bash
curl -X GET http://localhost:5000/user \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Servicio de Pedidos:
```bash
curl -X GET http://localhost:5000/order \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Servicio de Productos:
```bash
curl -X GET http://localhost:5000/product \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Ejemplos por Rol

#### Usuario Regular
Un usuario con rol "user" puede acceder a:
- /user
- /order
- /product

#### Administrador
Un usuario con rol "admin" puede acceder a todos los servicios, incluyendo:
- /user
- /order
- /product
- /database (sólo para administradores)

