# Project Delivery ## Arquitectura del Proyecto

El proyecto está diseñado utilizando una arquitectura de microservicios, donde cada componente tiene una responsabilidad específica y se comunica con otros servicios a través de APIs REST o mensajería basada en eventos. A continuación, se describen los componentes principales, sus responsabilidades, conexiones y dependencias.

---

### **Componentes Principales**

#### 1. **Cliente (Frontend)**
- **Descripción**: Interfaz de usuario desarrollada con React y TypeScript. Permite a los usuarios interactuar con la plataforma para explorar contenido, gestionar perfiles, realizar pagos y recibir recomendaciones.
- **Tecnologías**: React, TypeScript, Redux, Tailwind CSS, Vite, Nginx.
- **Conexiones**:
  - Consume las APIs de los microservicios: `auth-service`, `content-service`, `payment-service`, `recommender-service`.
- **Dependencias**:
  - APIs REST de los microservicios backend.

---

#### 2. **`auth-service`**
- **Descripción**: Gestiona la autenticación de usuarios, incluyendo registro, inicio de sesión, cierre de sesión y restablecimiento de contraseñas.
- **Tecnologías**: Node.js, Express, MongoDB, JWT, bcrypt, Twilio, Kafka.
- **Conexiones**:
  - Se comunica con `auth-mongodb` para almacenar credenciales y datos de autenticación.
  - Utiliza Kafka para enviar y recibir eventos relacionados con la autenticación.
  - Interactúa con Twilio para enviar mensajes de verificación.
- **Dependencias**:
  - MongoDB (`auth-mongodb`).
  - Kafka.
  - Twilio API.

---

#### 3. **`accounts-service`**
- **Descripción**: Administra las cuentas de usuario y perfiles. Permite la creación de hasta 5 perfiles por cuenta.
- **Tecnologías**: Node.js, Express, MySQL, Kafka.
- **Conexiones**:
  - Se comunica con `mysql` para almacenar información de cuentas y perfiles.
  - Utiliza Kafka para la comunicación de eventos.
- **Dependencias**:
  - MySQL.
  - Kafka.

---

#### 4. **`content-service`**
- **Descripción**: Proporciona contenido multimedia (películas y series) y gestiona la caché para mejorar el rendimiento.
- **Tecnologías**: Node.js, Express, MongoDB, Redis, Kafka.
- **Conexiones**:
  - Se comunica con `content-mongodb` para almacenar información del contenido.
  - Utiliza Redis para la caché de datos.
  - Consume la API externa de TMDB para obtener datos de películas y series.
  - Utiliza Kafka para la comunicación de eventos.
- **Dependencias**:
  - MongoDB (`content-mongodb`).
  - Redis.
  - Kafka.
  - TMDB API.

---

#### 5. **`payment-service`**
- **Descripción**: Gestiona los pagos y suscripciones de los usuarios. Soporta métodos de pago como Stripe y PayPal.
- **Tecnologías**: Node.js, Express, MongoDB, Stripe, PayPal, Kafka.
- **Conexiones**:
  - Se comunica con `payment-mongodb` para almacenar datos de pagos y suscripciones.
  - Utiliza Kafka para la comunicación de eventos.
  - Consume las APIs externas de Stripe y PayPal para procesar pagos.
- **Dependencias**:
  - MongoDB (`payment-mongodb`).
  - Kafka.
  - Stripe API.
  - PayPal API.

---

#### 6. **`recommender-service`**
- **Descripción**: Genera recomendaciones personalizadas basadas en el historial de contenido visto y las preferencias del usuario.
- **Tecnologías**: Node.js, Express, MongoDB, Groq AI, Kafka.
- **Conexiones**:
  - Se comunica con `recommender-mongodb` para almacenar datos de contenido "gustado" por los usuarios.
  - Utiliza Kafka para la comunicación de eventos.
  - Consume Groq AI para generar recomendaciones basadas en IA.
- **Dependencias**:
  - MongoDB (`recommender-mongodb`).
  - Kafka.
  - Groq AI.

---

#### 7. **`streamer-service`**
- **Descripción**: Proporciona la funcionalidad de transmisión de video (streaming) con soporte para diferentes calidades.
- **Tecnologías**: Node.js, Express.
- **Conexiones**:
  - No especificadas en el repositorio actual, pero probablemente interactúe con un sistema de almacenamiento de contenido multimedia.
- **Dependencias**:
  - No especificadas.

---

### **Infraestructura Compartida**

1. **Bases de Datos**:
   - **MongoDB**: Usado por `auth-service`, `content-service`, `payment-service`, `recommender-service`.
   - **MySQL**: Usado por `accounts-service`.

2. **Mensajería**:
   - **Kafka**: Usado para la comunicación de eventos entre los microservicios.

3. **Caché**:
   - **Redis**: Usado por `content-service` para mejorar el rendimiento.

4. **APIs Externas**:
   - **TMDB API**: Proporciona datos de películas y series. Consumida por `content-service`.
   - **Groq AI**: Genera recomendaciones personalizadas. Consumida por `recommender-service`.
   - **Stripe API**: Procesa pagos. Consumida por `payment-service`.
   - **PayPal API**: Procesa pagos. Consumida por `payment-service`.
   - **Twilio API**: Envía mensajes de verificación. Consumida por `auth-service`.

---

### **Conexiones entre Componentes**

- **Cliente (Frontend)**:
  - Consume las APIs REST de los microservicios (`auth-service`, `content-service`, `payment-service`, `recommender-service`).

- **Microservicios**:
  - Se comunican entre sí mediante Kafka para eventos como actualizaciones de usuarios, pagos realizados, o contenido agregado.

- **Servicios Externos**:
  - Los microservicios interactúan con APIs externas (TMDB, Groq AI, Stripe, PayPal, Twilio) para realizar operaciones específicas.

---

### **Diagrama de Arquitectura**

![diagrama](https://github.com/user-attachments/assets/329bba45-c3ac-4e66-968a-1bcae7dbc2fe)


## Docker

  ```bash
  docker build -t generator-app .
  docker run --rm -v $(pwd)/skeleton:/app/skeleton generator-ap
