Daniel Alejandro Rincón Rico

# Proyecto: API Gateway y Microservicios Seguros

Este proyecto implementa un sistema basado en un **API Gateway** que controla el acceso a tres microservicios. Se han aplicado estrategias de seguridad para garantizar la protección de los endpoints y los datos sensibles.

---

## **Estructura del Proyecto**

El proyecto está compuesto por los siguientes componentes:

1. **API Gateway (`api_gateway.py`)**:
   - Actúa como intermediario entre los clientes y los microservicios.
   - Implementa autenticación, autorización, validación de IPs y límites de solicitudes.
   - Genera jwt firmados con tiempo de expiración

2. **Microservicios**:
   - **`microservice.py`**: Proporciona un endpoint seguro con validación de certificados.
   - **`database.py`**: Simula un acceso seguro a una base de datos solo a usuarios administradores.
   - **`microservice_pay.py`**: Procesa pagos con validación de datos y encabezados y se puede usar solo por usuarios.

3. **Archivo de Configuración (`config.py`)**:
   - Carga las variables sensibles desde un archivo `.env` y disponibiliza función que limita acceso de IPS.

4. **Archivo `.env`**:
   - Contiene claves y certificados sensibles, como `SECRET_KEY`, `CERTIFICATE_DB`, `CERTIFICATE_MS`, y `CERTIFICATE_PAY` en un escenario real se puede controlar por ambiente y como secret.
---
## **Requisitos Previos**

1. **Python 3.8+**
2. Instalar las dependencias necesarias:
   ```bash
   - pip install flask flask-limiter python-dotenv requests
   
--- 
## **Ejecutar el proyecto**

1. Ejecutar cada microservicio en una terminal separada:

    ```bash
    - python microservice.py
    - python database.py
    - python microservice_pay.py
2. Iniciar el API Gateway:
   
    ```bash
    - python api_gateway.py
---
## **Probar el proyecto**
1. Generar token para administrador:
   
    ```bash
    - curl --location 'http://127.0.0.1:5000/login' \
    --header 'Content-Type: application/json' \
    --data '
    {
        "username": "admin",
        "password": "admin123"
    }'
2. Consultar servicio de base de datos atraves del gateway:
   
    ```bash
    curl --location 'http://127.0.0.1:5000/gateway/db' \
    --header 'Authorization: Bearer <Token>
    
3. Intentar consumir microservicio:
   
    ```bash
    curl --location 'http://127.0.0.1:5000/gateway/microservice' \
    --header 'Content-Type: application/json' \
    --header 'Authorization: ••••••'
    
4. Generar autenticación como cliente:
   
    ```bash
    curl --location 'http://127.0.0.1:5000/login' \
    --header 'Content-Type: application/json' \
    --data '{
        "username": "user1",
        "password": "password123"
    }'
5. Procesar pago como cliente:
    
    ```bash
    curl --location 'http://127.0.0.1:5000/gateway/microservice_pay' \
    --header 'Content-Type: application/json' \
    --header 'Authorization: Bearer <token>' \
    --data '{
        "mount": "800",
        "card": "32165"
    }'
6. Si se intenta consumir algún servicio con el curl:
   
    ```bash
        curl --location 'http://127.0.0.1:5003/microservice_pay' \
    --header 'Content-Type: application/json' \
    --header 'Authorization: Bearer <token>' \
    --data '{
        "mount": "800",
        "card": "32165"
    }'
Se obtiene la respuesta:


    {
        "error": "resource not found"
    }
