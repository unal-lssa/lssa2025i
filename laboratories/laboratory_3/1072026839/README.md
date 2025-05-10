# LSSA Lab 3 Project: Arquitectura con Load Balancer y API Gateway

## Carlos Alberto Arevalo Martinez

Este proyecto implementa una arquitectura de microservicios segura que incluye Frontend de Login, Frontend Principal, API Gateway, Load Balancer, múltiples Backends y una base de datos MySQL, todos orquestados con Docker Compose. El sistema utiliza TextX para la definición de arquitecturas mediante un lenguaje de dominio específico (DSL) e implementa el patrón de seguridad "Limit Exposure".

## TextX y DSL para Arquitecturas

El proyecto utiliza TextX para definir un Lenguaje de Dominio Específico (DSL) para modelar arquitecturas de software. Este enfoque aporta varias ventajas:

1. **Definición declarativa**: La arquitectura se define de manera clara y concisa en el archivo `model.arch`
2. **Validación automática**: TextX valida automáticamente que el modelo cumpla con las reglas definidas en la gramática
3. **Transformaciones de modelo**: El modelo validado se puede transformar fácilmente en diferentes artefactos (código, configuraciones, etc.)
4. **Abstracción**: El usuario final solo necesita entender el DSL, no los detalles técnicos de implementación

### Gramática del DSL (archivo `arch.tx`)

La gramática define:
- **Componentes**: Entidades como `frontend`, `backend`, `database`, `load_balancer` y `api_gateway`
- **Conectores**: Relaciones entre componentes como `http` y `db_connector`

### Implementación del Patrón de Seguridad "Limit Exposure"

Una característica principal de esta arquitectura es la implementación del patrón de seguridad "Limit Exposure" mediante el API Gateway:

- **Reducción de la superficie de ataque**: Solo el API Gateway y los frontends están expuestos al público.
- **Control de acceso centralizado**: Toda comunicación pasa a través del API Gateway, que implementa autenticación mediante JWT.
- **Protección de componentes críticos**: Los backends y la base de datos quedan ocultos detrás del API Gateway.

### Escalabilidad de Backends

Una característica notable del DSL es la capacidad de definir múltiples backends. Aunque el ejemplo muestra dos backends (`lssa_be1` y `lssa_be2`), el diseño permite:

- **Cantidad flexible**: Puedes añadir tantos backends como necesites modificando el archivo `model.arch`
- **Configuración automática**: El load balancer se configura automáticamente para distribuir carga entre todos los backends definidos
- **Relaciones dinámicas**: Los conectores definen explícitamente qué backends deben recibir tráfico del load balancer

Para añadir más backends, simplemente se modifica el modelo:

```
# Añadir en model.arch
component backend lssa_be3
component backend lssa_be4

# Y conectar 
connector http lssa_lb -> lssa_be3
connector http lssa_lb -> lssa_be4
connector db_connector lssa_be3 -> lssa_db
connector db_connector lssa_be4 -> lssa_db
```

El transformador generará automáticamente todo el código y configuración necesarios sin cambios adicionales.

## Estructura del Proyecto

La arquitectura sigue el siguiente flujo:

```
Frontend Login → API Gateway → Frontend Principal → API Gateway → Load Balancer → Backends (múltiples) → Database
```

### Componentes

- **Login Frontend**: Aplicación Node.js con Express que proporciona una interfaz de autenticación
- **Frontend Principal**: Aplicación Node.js con Express que proporciona la interfaz para interactuar con el sistema después de la autenticación
- **API Gateway**: Servicio Flask que implementa autenticación JWT y limita la exposición de los componentes internos
- **Load Balancer**: Servidor NGINX que distribuye el tráfico entre múltiples backends
- **Backends**: Servicios Flask (Python) que procesan peticiones y se comunican con la base de datos (escalable a N instancias)
- **Database**: Instancia MySQL para almacenamiento persistente

## Tecnologías Utilizadas

- **TextX**: Framework para crear lenguajes de dominio específico (DSL) en Python que facilita la definición de gramáticas personalizadas y la generación de metamodelos
- **Docker**: Contenedores para cada componente
- **Docker Compose**: Orquestación de la infraestructura
- **NGINX**: Load balancer para distribuir cargas
- **Flask**: Framework para los backends y el API Gateway
- **JWT**: JSON Web Tokens para autenticación segura
- **Express.js**: Framework para los frontends
- **MySQL**: Base de datos relacional

## Implementación del API Gateway

El API Gateway se implementa utilizando Flask con las siguientes características:

1. **Autenticación mediante JWT**: Proporciona tokens de acceso después de verificar credenciales
2. **Limitación de Exposición**: Verifica la IP de origen de las peticiones
3. **Control de Acceso**: Utiliza decoradores para proteger rutas específicas
4. **Proxy Transparente**: Redirige peticiones autenticadas al Load Balancer

## Implementación del Load Balancer

El load balancer se implementa utilizando NGINX con la siguiente configuración:

1. **Round-Robin**: Distribuye las peticiones de manera equitativa entre los backends
2. **Health Checks**: Detecta automáticamente si un backend deja de responder
3. **Transparencia**: Los backends no necesitan conocer el balanceador

## Estructura del Proyecto

```
lssa-lab3/
├── arch.tx                 # Gramática del DSL
├── Dockerfile              # Dockerfile para el generador
├── generation.py           # Script de generación
├── metamodel.py            # Definición del metamodelo
├── model.arch              # Definición de la arquitectura
├── transformations.py      # Transformaciones de modelo a código
└── skeleton/               # Código generado
    ├── docker-compose.yml
    ├── lssa_login_fe/      # Frontend de Login
    ├── lssa_fe/            # Frontend Principal
    ├── lssa_api_gw/        # API Gateway
    ├── lssa_lb/            # Load Balancer (NGINX)
    ├── lssa_be1/           # Backend 1
    ├── lssa_be2/           # Backend 2
    └── lssa_db/            # Database
```

## Generación del Código

El proyecto utiliza transformaciones modelo-a-texto (M2T) para generar automáticamente todos los artefactos necesarios a partir del modelo DSL:

1. **Archivos de configuración Docker** para cada componente
2. **Código fuente** de cada componente:
   - API Gateway con autenticación JWT
   - Frontend de Login para autenticación de usuarios
   - Frontend Principal con token en cabeceras HTTP
   - Configuración NGINX con upstream servers para todos los backends definidos
   - Código Flask para cada backend
   - Scripts SQL para inicialización de base de datos
3. **Docker Compose** para orquestar todo el sistema

### Proceso de Transformación

El proceso de transformación ocurre en varias etapas:

1. **Parsing del modelo**: TextX interpreta el archivo `model.arch` según la gramática definida
2. **Validación**: Se verifican las relaciones y tipos de componentes
3. **Recolección de metadatos**: Se identifican los backends, frontends, y otros componentes
4. **Generación de código**: Para cada componente identificado, se genera código específico
5. **Orquestación**: Se genera el archivo docker-compose.yml con todas las dependencias

Esta aproximación basada en modelos permite extender y modificar la arquitectura simplemente cambiando el archivo `model.arch` y ejecutando nuevamente el generador.

## Pasos para Ejecutar el Proyecto

### 1. Construir la imagen del generador

```bash
docker build -t lssa-lab3 .
```

### 2. Generar el código

```bash
docker run --rm -v ${PWD}:/app lssa-lab3
```

Este comando crea la carpeta `skeleton/` con todos los archivos necesarios.

### 3. Ejecutar el sistema completo

```bash
cd skeleton
docker-compose up --build
```

### 4. Acceder a la aplicación

1. Accede al frontend de login:
   ```
   http://localhost:8001/
   ```

2. Inicia sesión con las credenciales predeterminadas:
   - Usuario: `user1`
   - Contraseña: `password123`

3. Serás redirigido automáticamente al frontend principal (puerto 8002) con un token JWT válido en la URL.

4. Ahora puedes interactuar con el sistema, y todas las peticiones incluirán automáticamente el token JWT para autenticación.

## Ventajas de la Arquitectura con API Gateway

La incorporación del API Gateway a la arquitectura aporta importantes beneficios de seguridad:

1. **Punto único de entrada**: Toda comunicación con los servicios internos pasa por el API Gateway
2. **Autenticación centralizada**: El manejo de tokens JWT se concentra en un único componente
3. **Menor superficie de ataque**: Los componentes críticos (backends, base de datos) no son accesibles directamente
4. **Control granular**: Se pueden aplicar políticas de seguridad específicas para cada ruta
5. **Auditoría simplificada**: Es más fácil registrar y monitorear todo el tráfico entrante

## Ventajas del Enfoque DSL para Arquitecturas

La combinación de TextX y el DSL personalizado para definir arquitecturas ofrece importantes ventajas:

1. **Abstracción de la complejidad**: Los detalles técnicos de la configuración NGINX, Docker y el código se generan automáticamente
2. **Comunicación efectiva**: El modelo sirve como documentación clara y concisa de la arquitectura
3. **Flexibilidad para escalar**: Agregar nuevos componentes es tan simple como modificar el modelo DSL
4. **Consistencia**: Todos los componentes se generan siguiendo los mismos patrones y estándares
5. **Evolución dirigida por modelo**: Cambios en la arquitectura se implementan modificando el modelo, no el código

## Conclusión

Este proyecto demuestra una arquitectura moderna con seguridad incorporada desde el diseño, utilizando el poder de los lenguajes específicos de dominio (DSL). La implementación del patrón "Limit Exposure" a través del API Gateway muestra cómo se pueden aplicar tácticas de seguridad en el nivel arquitectónico.

La arquitectura resultante proporciona un sistema con alta disponibilidad, escalabilidad y seguridad, donde los componentes críticos están protegidos detrás de capas de autenticación y autorización. El uso del enfoque basado en modelos facilita la evolución y mantenimiento del sistema, permitiendo cambios arquitectónicos significativos con modificaciones mínimas al código fuente.