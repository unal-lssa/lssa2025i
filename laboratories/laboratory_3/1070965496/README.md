# Laboratorio 3 - Seguridad

### Juan David Ramírez Ávila

Este laboratorio presenta una simulación de una arquitectura de microservicios utilizando python. Se enfoca en la comunicación entre servicios independientes, gestión de logs, notificaciones y uso de una puerta de enlace (`API Gateway`), resaltando tácticas de seguridad vistas durante el módulo.

## Estructura del Proyecto

```
Laboratorio3/
├── api_gateway.py               
├── database.py                  
├── database_logging.py          
├── logging_service.py          
├── microservice.py              
├── notification_service.py    
```

## Descripción de los Componentes

- **API Gateway (`api_gateway.py`)**: Punto central para recibir solicitudes externas. Redirige las solicitudes a los microservicios adecuados.
- **Logging Service (`logging_service.py`)**: Se encarga de registrar eventos o errores del sistema en la base de datos.
- **Notification Service (`notification_service.py`)**: Encargado de enviar notificaciones (por ejemplo, correos o alertas) en respuesta a ciertos eventos.
- **Microservice (`microservice.py`)**: Microservicio central de la arquitectura 
- **Database Modules (`database.py`, `database_logging.py`)**: Manejan la conexión y operaciones básicas con las bases de datos.


## Beneficios de seguridad con los componentes y modificaciones realizadas 

### API Gateway – Seguridad Implementada

El API Gateway escrito con Flask de este laborario, implementa diferentes mecanismos de seguridad que refuerzan el principio de **"Limit Exposure"**, asegurando que solo usuarios autorizados accedan a recursos protegidos, y que los microservicios internos estén debidamente resguardados.

### Mecanismos de Seguridad

#### 1. Autenticación mediante tokens
- Requiere que las peticiones incluyan un token.
- El token es verificado con una clave secreta (`HS256`).
- Extrae los datos del usuario (`username`, `role`) para usarlos en la sesión.

#### 2. Autorización basada en roles
- El endpoint `/data` solo puede ser accedido por usuarios con el rol `admin`.
- Otros roles reciben un `403 Forbidden`.

#### 3. Limitación de exposición por IP
- Se restringe el acceso a los endpoints protegidos únicamente a una IP autorizada (`127.0.0.1`).
- Si la IP de origen no coincide, se responde con `403 Forbidden`.

#### 4. Rate Limiting (Límites de uso)
- **Login:** Máximo 5 intentos por minuto por dirección IP.
- **Endpoints protegidos:** Máximo 100 solicitudes por hora por usuario autenticado.
- Implementado con `Flask-Limiter`.

#### 5. Registro de auditoría (Audit Logging)
- Cada acceso a `/data` o `/microservice-data` es reportado al servicio de logging (`http://127.0.0.1:5004/log`).
- Los logs incluyen el usuario y la acción realizada.

#### 6. Acceso indirecto a microservicios
- El endpoint `/microservice-data` actúa como proxy seguro hacia un microservicio interno (`http://127.0.0.1:5001/microservice`).
- Este microservicio no está expuesto directamente al exterior, sino que es controlado por el gateway.

####  Tácticas de Seguridad Aplicadas

| Táctica                    | Implementación                              |
|---------------------------|---------------------------------------------|
| Autenticación             | JWT Tokens                                  |
| Autorización              | Roles (`admin` requerido para `/data`)      |
| Limitación de Exposición  | Filtro por IP (`@limit_exposure`)           |
| Control de Frecuencia     | Rate limiting con Flask-Limiter             |
| Trazabilidad              | Registro de accesos en microservicio de log |
| Encapsulamiento de acceso | Gateway como proxy hacia microservicios     |


## Requisitos

- Python 3.x
- `pip` para gestionar paquetes

### Dependencias recomendadas

```bash
pip install flask
pip install requests
pip install pyjwt
```

## Ejecución del Laboratorio

### Paso 1: Clonar o descomprimir el proyecto

Asegúrate de tener todos los archivos en el mismo directorio:

```
Laboratorio3/
```

### Paso 2: Ejecutar los archivos .py 

En diferentes terminales, ejecuta cada uno de los microservicios:

1. **Servicio de Logs**
   ```bash
   python logging_service.py
   ```

2. **Servicio de Notificaciones**
   ```bash
   python notification_service.py
   ```

3. **Servicio Principal**
   ```bash
   python microservice.py
   ```

4. **API Gateway**
   ```bash
   python api_gateway.py
   ```
5. **Base de datos principal**
   ```bash
   python database.py
   ```
6. **Base de datos con datos de Logging**
   ```bash
   python database_logging.py
   ```

### Paso 3: Probar el acceso a través del API Gateway

Se usa el siguiente comando, con el fin de generar un token:

```bash
curl -X POST http://127.0.0.1:5000/login \
-H "Content-Type: application/json" \
-d '{"username": "user1", "password": "password123"}'   
 ```

 Se espera se genere un token: 

```json
{"token": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."}
```

Ahora, con el token obtenido y el siguiendte comando se accede a /data: 

```bash
curl http://127.0.0.1:5000/data \
-H "Authorization: Bearer TU_TOKEN_AQUI"
 ```

Se espera la siguiente salida: 

```json
{
  "message": "Data accessed successfully!"
}
```

Entonces, si se repite el proceso anterior, pero usando el usuario user2, la salida obtenida es: 

```json
{
  "message": "Forbidden: Admins only"
}
```
Esto, ocurre porque se esta aplicando un táctica de seguridad de autorización basada en roles. 

Otras pruebas, interesantes a revisar, son las enfocadas en la táctica de Rate limiting, esto con el fin de proteger el sistema a un ataque de DoS (Denial of Service). 

1. Número de peticiones a tráves de la misma IP, con el siguiente comando se simula: 

```bash
for i in {1..6}; do
  curl http://127.0.0.1:5000/data &
done
 ```
Acá, se van a generar 5 tokens y el sexto, vamos a tener el mesaje o error: 429 Too Many Requests

2. Número de solicitudades a tráves del mismo usuario, con el siguiente comando se simula el esceneario: 

```bash
for i in {1..100}; do
  curl http://127.0.0.1:5000/data \
  -H "Authorization: Bearer TU_TOKEN_VALIDO"
  echo ""
done
 ```

 Acá, se van a generar 100 peticiones exitosas y en la 101, se obtiene el mensaje o error: 429 Too Many Requests

## Conclusiones 

El laboratorio tres evidencia de forma práctica y con un escenario tanto simplificado como sencillo, como una arquitectura de microservicios se beneficia del uso de un **API Gateway** como orquestador central de acceso a los componentes del sistema. A través de la implementación de diversas tácticas, como **autenticación**, **autorización basada en roles**, **limitación de exposición por IP**, y **Rate Limiting**, aseguran que los recursos estén protegidos contra accesos no autorizados y abusos.

Además, se resalta la inclusión de registros de auditoría garantizando la trazabilidad en los accesos a los servicios, cumpliendo con prácticas recomendadas en los sistemas distribuidos.

El enfoque indirecto hacia microservicios internos, canalizando todas las solicitudes a través del gateway, fortalece el principio de **"Limit Exposure"** al evitar exponer directamente los servicios sensibles al exterior.

En resumen, este laboratorio refuerza la importancia de incorporar mecanismos de seguridad desde el diseño de una arquitectura de software distribuida, destacando cómo prácticas concretas mitigan riesgos comunes en entornos reales.
