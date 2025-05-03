Daniel Alejandro Rincón Rico


# Proyecto: API Gateway y Microservicios Seguros

Este proyecto implementa un sistema basado en un **API Gateway** que controla el acceso a múltiples microservicios. Se han aplicado estrategias de seguridad para garantizar la protección de los endpoints y los datos sensibles. Además, se ha ampliado el diseño para incluir un **balanceador de carga** y un **sistema de almacenamiento en caché**.

---

## **Estructura del Proyecto**

El proyecto está compuesto por los siguientes componentes:

1. **Balanceador de Carga (`load_balancer.py`)**:
   - Distribuye las solicitudes entre múltiples instancias del API Gateway utilizando un algoritmo de **round-robin**.

2. **API Gateway (`api_gateway.py`)**:
   - Actúa como intermediario entre los clientes y los microservicios.
   - Implementa autenticación, autorización, validación de IPs, límites de solicitudes y almacenamiento en caché.

3. **Microservicio de Caché (`cache_service.py`)**:
   - Proporciona almacenamiento temporal para datos consultados frecuentemente.

4. **Microservicios**:
   - **`microservice.py`**: Proporciona un endpoint seguro con validación de certificados.
   - **`database.py`**: Simula un acceso seguro a una base de datos solo a usuarios administradores.
   - **`microservice_pay.py`**: Procesa pagos con validación de datos y encabezados y se puede usar solo por usuarios.

5. **Archivo de Configuración (`config.py`)**:
   - Carga las variables sensibles desde un archivo `.env` y disponibiliza función que limita acceso de IPs.

6. **Archivo `.env`**:
   - Contiene claves y certificados sensibles, como `SECRET_KEY`, `CERTIFICATE_DB`, `CERTIFICATE_MS`, y `CERTIFICATE_PAY`. En un escenario real, se puede controlar por ambiente y como secret.

---

## **Requisitos Previos**

1. **Python 3.8+**
2. Instalar las dependencias necesarias:
   ```bash
   pip install flask flask-limiter python-dotenv requests
   ```

---

## **Ejecutar el Proyecto**

1. Ejecutar cada microservicio en una terminal separada:

    ```bash
    python microservice.py
    python database.py
    python microservice_pay.py
    python cache_service.py
    ```

2. Iniciar múltiples instancias del API Gateway:
    ```bash
    python api_gateway.py --port 5000
    python api_gateway.py --port 5001
    ```

3. Iniciar el balanceador de carga:
    ```bash
    python load_balancer.py
    ```

---

## **Probar el Proyecto**

1. Generar token para administrador:
    ```bash
    curl --location 'http://127.0.0.1:8000/login' \
    --header 'Content-Type: application/json' \
    --data '{
        "username": "admin",
        "password": "admin123"
    }'
    ```

2. Consultar servicio de base de datos a través del gateway:
    ```bash
    curl --location 'http://127.0.0.1:8000/gateway/db' \
    --header 'Authorization: Bearer <Token>'
    ```

3. Intentar consumir microservicio:
    ```bash
    curl --location 'http://127.0.0.1:8000/gateway/microservice' \
    --header 'Content-Type: application/json' \
    --header 'Authorization: Bearer <Token>'
    ```

4. Generar autenticación como cliente:
    ```bash
    curl --location 'http://127.0.0.1:8000/login' \
    --header 'Content-Type: application/json' \
    --data '{
        "username": "user1",
        "password": "password123"
    }'
    ```

5. Procesar pago como cliente:
    ```bash
    curl --location 'http://127.0.0.1:8000/gateway/microservice_pay' \
    --header 'Content-Type: application/json' \
    --header 'Authorization: Bearer <Token>' \
    --data '{
        "mount": "800",
        "card": "32165"
    }'
    ```

6. Consultar datos con almacenamiento en caché:
    ```bash
    curl --location 'http://127.0.0.1:8000/data' \
    --header 'Authorization: Bearer <Token>'
    ```

    - Si los datos están en la caché:
      ```json
      {
          "cached": true,
          "data": "valor_en_cache"
      }
      ```

    - Si los datos no están en la caché:
      ```json
      {
          "cached": false,
          "data": "valor_de_la_base_de_datos"
      }
      ```

---

## **Notas Adicionales**

- El balanceador de carga distribuye las solicitudes entre las instancias del API Gateway en los puertos `5000` y `5001`.
- El sistema de caché reduce la carga en la base de datos y mejora el tiempo de respuesta para solicitudes repetidas.
- Asegúrate de proteger el archivo `.env` y excluirlo del control de versiones (`.gitignore`).
- En un entorno de producción, se recomienda usar HTTPS para cifrar las comunicaciones.

---

## **Diagrama**

<img width="908" alt="Captura de pantalla 2025-05-02 231356" src="https://github.com/user-attachments/assets/878cc2f5-1bf9-47ea-a70e-6376d900e805" />

