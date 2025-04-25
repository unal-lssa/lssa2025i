
Rodriguez Martinez Diego Alejandro
1073252824

# Arquitectura de Microservicios

Esta es una arquitectura basada en microservicios con una API Gateway, un microservicio, y un servicio de login que maneja la autenticación de usuarios. 

## Servicios

### 1. **API Gateway (Puerto 5000)**
La API Gateway actúa como un punto de entrada único para todas las solicitudes. Redirige las peticiones a los microservicios correspondientes.

Para iniciar la API Gateway:
```bash
python api_gateway.py
```

La API Gateway estará disponible en [http://localhost:5000](http://localhost:5000).

### 2. **Microservicio (Puerto 5001)**
El microservicio maneja la lógica de negocio y las operaciones de los datos.

Para iniciar el microservicio:
```bash
python microservice.py
```

El microservicio estará disponible en [http://localhost:5001](http://localhost:5001).

### 3. **Servicio de Login (Puerto 5003)**
El servicio de login maneja la autenticación de usuarios y genera un token JWT que incluye control de expiración. Los tokens generados ahora deben ser enviados con el prefijo `Bearer`.

Para iniciar el servicio de login:
```bash
python login_service.py
```

El servicio de login estará disponible en [http://localhost:5003](http://localhost:5003).

### Cambios importantes:
- **Control de usuarios**: El servicio de login ahora gestiona las credenciales y genera un token JWT para autenticación.
- **Control de expiración de tokens**: Los tokens tienen fecha de expiración y se validan.
- **Prefijo `Bearer` en el token**: Los tokens deben incluir el prefijo `Bearer` al enviarlos en la cabecera `Authorization`.

## Iniciar todos los servicios

Ejecute los siguientes comandos en terminales independientes para iniciar cada servicio:

1. **API Gateway**:
```bash
python api_gateway.py
```

2. **Microservicio**:
```bash
python microservice.py
```

3. **Servicio de Login**:
```bash
python login.py
```

## Notas adicionales

- Asegúrese de que los puertos no entren en conflicto.
- Los tokens deben incluir el prefijo `Bearer` en la cabecera `Authorization`.

