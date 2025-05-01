# Laboratorio 3 - Limitación de Exposición con API Gateway

**Nombre completo:** [Yilver Alirio Ramírez Ochoa]

## Descripción general

Este laboratorio demuestra cómo aplicar la táctica de seguridad *Limit Exposure* (Limitación de exposición) en una arquitectura de microservicios, utilizando el patrón arquitectónico API Gateway para reducir la superficie de ataque y centralizar el control de acceso.

## Arquitectura implementada

- **API Gateway** (puerto 5000): punto de entrada seguro al sistema. Aplica validación por IP y autenticación JWT.
- **Microservicio** (puerto 5001): servicio de lógica de negocio.
- **Base de datos simulada** (puerto 5002): servicio que representa una base de datos protegida.
- **Servicio de auditoría** (puerto 5004): nuevo servicio agregado, accesible solo por usuarios administradores.

## Pasos para ejecutar

1. Abre cuatro terminales y ejecuta cada servicio por separado:

    - API Gateway:
      ```bash
      python api_gateway.py
      ```

    - Microservicio:
      ```bash
      python microservice.py
      ```

    - Base de datos:
      ```bash
      python database.py
      ```

    - Servicio de auditoría:
      ```bash
      python audit.py
      ```

2. Solicita un token JWT:

    Para usuario normal:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d "{\"username\": \"user1\", \"password\": \"password123\"}" http://127.0.0.1:5000/login
    ```

    Para usuario administrador:
    ```bash
    curl -X POST -H "Content-Type: application/json" -d "{\"username\": \"admin\", \"password\": \"adminpass\"}" http://127.0.0.1:5000/login
    ```

3. Accede a los endpoints protegidos:

    Acceso al servicio de datos:
    ```bash
    curl -X GET -H "Authorization: Bearer <tu_token>" http://127.0.0.1:5000/data
    ```

    Acceso al servicio de auditoría (solo para admin):
    ```bash
    curl -X GET -H "Authorization: Bearer <tu_token_admin>" http://127.0.0.1:5000/audit
    ```

## Mejoras realizadas

- Se agregó un nuevo microservicio: **Servicio de Auditoría**.
- Se creó una regla adicional que permite acceder al endpoint `/audit` solo si el usuario autenticado es `admin`.
- Se mantuvieron las validaciones por IP (`127.0.0.1`) y el uso de JWT para control de acceso.
- Se reforzó la arquitectura sin aumentar la complejidad del diseño.

## Conclusión

Este laboratorio demuestra cómo aplicar seguridad desde la etapa de diseño (*Secure by Design*), mediante el uso de un API Gateway que limita el acceso directo a los servicios y aplica reglas centralizadas de control. La adición de servicios específicos y validaciones basadas en roles refuerza el principio de *Limit Exposure*, fundamental en arquitecturas seguras a gran escala.
