# Arquitectura distribuida basada en microservicios para un E-commerce 

#### Sergio Andrés Cabezas
#### Jilkson Alejandro Pulido Cruz
#### Diego Alejandro Rodriguez Martinez
#### Yosman Alexis Arenas Jimenez
#### Juan David Ramírez Ávila

## Link Colab: https://colab.research.google.com/drive/1vmXCFLSbaahkZ9xu_FgspS2BZzbGXwS7?usp=sharing

---
El objetivo principal de esta segunda entrega es realizar un proceso iterativo de diseño parcial y verificación de la arquitectura distribuida basada en microservicios para un E-commerce, que se propuso en la primera entrega, mediante un enfoque práctico y estructurado que permita evaluar atributos de calidad clave como la seguridad y la escalabilidad.


## 1. Visión general
La arquitectura propuesta para el sistema de e-commerce se basa en principios de **microservicios desacoplados**, altamente escalables y seguros. El diseño permite gestionar de manera independiente cada dominio de negocio: usuarios, pedidos, productos, inventario y pagos, con comunicación eficiente a través de protocolos adecuados, como HTTP para interacciones tradicionales y MQTT para los eventos relacionados con el servicio de pagos.

El flujo completo desde el cliente hasta el procesamiento de pagos se maneja de forma **modular**, mejorando la resiliencia, seguridad, escalabilidad y mantenibilidad del sistema.


## 2. Arquitectura del sistema 

A continuación, se presenta un diagrama de arquitectura de componentes y conectores, que se expuso en la primera entrega del proyecto. 

![Texto alternativo de la imagen](imagenes/Arquitectura.png)

Adicionalmente, utilizando las librerías de grafos vistas en clase también se construyó el diagrama de componentes y conectores, como se aprecia seguidamente: 

![Texto alternativo de la imagen](imagenes/ArquitecturaProyectoGrafos.png)


## 3. Flujo elegido de la arquitectura del sistema 

Para realizar el proceso de verificación de los atributos de seguridad y escalabilidad, se eligió el flujo de la arquitectura que va desde el API Gateway —encargado de recibir las solicitudes del frontend— hasta el balanceador de carga, que distribuye las peticiones entre los microservicios. En el contexto de este proyecto, el proceso de verificación se centrará únicamente en el microservicio de usuarios. Consecutivamente, se presenta una imagen con la extracción, de la parte de la arquitectura a analizar: 


![Texto alternativo de la imagen](imagenes/FlujoSimplificado.png)


## 4. Iteración 1 

La arquitectura seleccionada corresponde a un fragmento clave para el correcto funcionamiento de un e-commerce. En el flujo arquitectónico elegido se aplican principios de **arquitectura** con énfasis en los atributos de calidad de:

- **Escalabilidad**: Capacidad de adaptarse a aumentos en la carga de trabajo de forma eficiente.
- **Seguridad**: Protección frente a accesos no autorizados y ataques comunes, garantizando confidencialidad, integridad y disponibilidad.

### 4.1 Componentes y tácticas asociadas

En este apartado del documento, se presenta una breve descripción de cada uno de los componentes del flujo arquitectónico elegido para desarrollar la iteración uno. 

#### 4.1.1. Frontend (`ecommerce_fe`)

- Aplicación web que ofrece la **interfaz gráfica** al usuario.
- Se encarga de mostrar productos, gestionar carritos, pagos y confirmar órdenes.
- **No contiene lógica de negocio crítica**; actúa como intermediario enviando solicitudes al **API Gateway**.
- Se comunica exclusivamente mediante **HTTP** con el API Gateway.

#### 4.1.2. **API Gateway** (`ecommerce_ag_us`)

- Es el punto de entrada al sistema. Filtra, enruta y valida solicitudes provenientes del cliente.
---

#### 4.1.3. **Balanceador de Carga** (`ecommerce_lb`)

-  Distribuye solicitudes entrantes de forma equitativa entre las instancias del microservicio de usuarios.
---

#### 4.1.4. **Microservicio de Usuarios**  

- Gestionar operaciones de usuarios (registro, login, modificación de datos, etc.).
---

#### 4.1.5. **Base de Datos de Usuarios** (`ecommerce_be_usr_db`)

-  Almancenar los datos de usuarios.

---

Al analizar el flujo arquitectónico elegido en la primera entrega, se observa que el sistema carece de un mecanismo de control de frecuencia, es decir, no existen límites definidos para el uso de los recursos o el número de solicitudes permitidas en un periodo de tiempo. Esta ausencia deja al sistema vulnerable a ataques de Denegación de Servicio (DoS), donde un atacante podría saturar los servicios mediante solicitudes excesivas, comprometiendo tanto la disponibilidad como la estabilidad del sistema. 

Por lo tanto, se simula un ataque de Denegación de Servicio (DoS) sobre el flujo seleccionado del sistema. En este escenario, se modela una situación en la que el sistema recibe N solicitudes concurrentes, sin contar con mecanismos de protección. Cada solicitud sigue una ruta aleatoria desde el frontend hasta la base de datos, exponiendo así las debilidades de la arquitectura ante cargas excesivas y mostrando la necesidad de implementar tácticas de seguridad.

Con base en la simulación, se aprecia, que al exponer al sistema a una gran cantidad de peticiones, la mayoría de estas fallan, por ejemplo, al simular 1000 solicitudes simultáneas, fallaron 754 (75,4%) y 246 exitosas, fueron (32.6 %), con esto se evidencia la necesidad, de aplicar una táctica de seguridad con el objetivo, de que el sistema, sea capaz de soportar, grandes cantidades de solicitudes concurrentes. Lo descrito, se confirma con la gráfica, que se presenta a continuación:  


![Texto alternativo de la imagen](imagenes/Sin_rate_limit.png)

Adicionalmente, en la siguiente gráfica es posible apreciar los fallos por componente reportados por la simulación, en la que se aprecia, que la mayoría de las fallas se dieron el el microservicio de usuarios, seguido por las fallas que se reportaron en el balanceador de carga. 

![Texto alternativo de la imagen](imagenes/FallosComponenteI1.png)


## 5. Iteración 2

En esta segunda iteración se introduce una táctica arquitectónica orientada a **mitigar vulnerabilidades de seguridad**, específicamente aquellas asociadas con ataques de **Denegación de Servicio (DoS)** o **Denegación de Servicio Distribuido (DDoS)**. 

Durante la **Iteración 1**, se evidenció que la arquitectura inicial no implementaba ningún tipo de **control de frecuencia de solicitudes**, lo que la dejaba completamente expuesta a este tipo de amenazas. Como respuesta, se decidió implementar una **táctica de seguridad conocida como _Rate Limiting_**, que permite regular el tráfico entrante hacia el sistema.

### 5.1 ¿Qué es *Rate Limiting* y por qué es una táctica arquitectónica?

 **Rate Limiting** es una **táctica arquitectónica de seguridad** ampliamente adoptada para controlar el número de solicitudes que una entidad (usuario, IP, sistema externo) puede realizar en un período determinado. Esta táctica permite:

- **Reducir la superficie de ataque**, evitando que actores maliciosos sobrecarguen el sistema.
- **Preservar la disponibilidad** de servicios críticos ante condiciones de alto tráfico.
- **Estabilizar la carga del sistema**, especialmente cuando se trabaja con recursos limitados como conexiones a base de datos o hilos de procesamiento.

En este contexto, Rate Limiting se ubica en la capa del **API Gateway**, el punto de entrada del sistema. Allí, actúa como **primer filtro**, evaluando si cada nueva solicitud debe ser aceptada o rechazada, en función de la carga actual del sistema.

En la simulación se lanzaron 1000 solicitudes concurrentes,  y se obtuvieron los resultados que se aprecian en la siguiente gráfica: 

![Texto alternativo de la imagen](imagenes/TransaccionesRateLimit.png)

En la gráfica de "Transacciones con Rate Limiting (Iteración 2)", se aprecia que al aplicar la táctica arquitectónica de Rate Limiting, se aprecia que 30 solicitudes, fueron exitosas y el resto debe esperar o será descartado si no hay capacidad. De esta forma, se evita que el sistema colapse en caso de que reciba un gran número de peticiones concurrentes. 

Adicionalmente, se presenta la gráfica "Fallos por componente (con Rate Limiting)", en la que se visualiza, que el número de fallos disminuye en relación a la gráfica "Fallos por componente (Iteración 1)", y la mayoría de las fallas se dan en el micro-servicio de usuarios,seguido del balanceador de carga.  

![Texto alternativo de la imagen](imagenes/FallosComponenteRL.png)

### 5.2 Flujo Arquitectónico Simulado

1. Una solicitud ingresa al sistema por el **frontend**.
2. Llega al **API Gateway**, donde se aplica la táctica de **Rate Limiting**.
3. Si la solicitud **se aprueba**, se enruta hacia el **microservicio de usuarios** y, finalmente, hacia una **base de datos**.
4. Si **no se aprueba** (por sobrepasar el límite), la solicitud se **rechaza inmediatamente**.


### 5.3 Impacto Arquitectónico

La inclusión del **Rate Limiting** como táctica aporta varias mejoras notables:

- **Robustez** frente a amenazas externas.  
- **Aislamiento y protección** de servicios internos.  
- **Desacoplamiento** de responsabilidades entre gateway y backend.  
- **Mayor resiliencia** ante tráfico irregular o malicioso.

Desde el punto de vista del diseño arquitectónico, esta iteración no solo **mitiga un riesgo** identificado previamente, sino que introduce un **patrón emergente de defensa perimetral**, reforzando el principio de **"defense in depth"**.

## 6. Iteración 3

En esta iteración se simuló un entorno donde el sistema fue sometido a una carga elevada de solicitudes concurrentes (por ejemplo, peticiones HTTP, trabajos de procesamiento de datos, eventos, etc.) sin ningún mecanismo automático de escalado (horizontal o vertical). A medida que ciertos componentes alcanzan sus límites de capacidad, comienzan a **rechazar solicitudes**, generando **cuellos de botella**, **degradación del servicio** y eventualmente **fallos sistémicos**.

Esto expone una arquitectura **sin capacidad de resiliencia** y, más importante aún, **sin tácticas arquitectónicas de escalabilidad implementadas**, lo que se traduce en un **sistema cero porciento resiliente** frente a aumentos repentinos de demanda.

### 6.1. Objetivos de la Simulación

- Identificar **puntos críticos** de la arquitectura bajo alta demanda.
- Validar que la ausencia de escalamiento provoca una **degradación no controlada del servicio**.
- Demostrar la importancia de incluir **tácticas de escalabilidad** en el diseño desde las etapas tempranas.

### 6.2 Resultados de la simulación

Se simularon 2.000 transacciones, de las cuales 1818 fallaron (90,9 %) y solo 182 fueron exitosas (9,1 %). Esto evidencia que, al no contar con una estrategia de escalabilidad, el sistema no puede manejar una carga excesiva de solicitudes, provocando inevitablemente un alto porcentaje de fallos. En la imagen, que se presenta seguidamente, se confirma lo mencionado. 

![Texto alternativo de la imagen](imagenes/Transacciones3.png)

Adicionalmente, también se revisaron los resultados obtenidos de las fallas por componente, donde se aprecia que en el fronted, fallaron 1131 (56.55%), en el microservicio de usarios 655 (32.75 %) y en el balanceador de carga 32 (1,6%). En la imagen que se muestra a continuación, se confirma lo descrito. 

![Texto alternativo de la imagen](imagenes/Componentes3.png)

Entonces, dado el alto porcentaje de transacciones fallidas (90,9 %) se ve la necesidad de aplicar una táctica de escalado arquitectónica, con el fin de que el sistema, funcione sin inconvenientes cuando sea sometido al altas cargas de trabajo. 

## 7. Iteración 4

Tras identificar el problema de saturación en el sistema, se opta por implementar una táctica de **autoescalado** para los componentes backend. Esta estrategia permite que, ante un aumento en la carga, se creen automáticamente nuevas réplicas de los componentes comprometidos. Estas réplicas son gestionadas por el **balanceador de carga**, que distribuye el tráfico de manera uniforme entre ellas. De este modo, el sistema mejora su **capacidad de respuesta**, manteniendo una **alta disponibilidad** y reforzando su **resiliencia operativa** ante variaciones en la demanda.

### 7.1. Objetivos de la simulación

### Objetivos de la Simulación con Autoescalado

- Medir cómo los componentes backend manejan cargas concurrentes y cómo el autoescalado contribuye a mantener el rendimiento.

- Observar si los componentes se escalan automáticamente, ajustando dinámicamente su capacidad.

### 7.2 Resultados de la simulación

Se simularon 2.000 transacciones, de las cuales 1996 fueron exitosas (99,8 %) y solo 4 fueron fallidas (0,2%). Esto evidencia que, el incluir una táctica arquitectónica, como el escalado hace que el sistema, sea mucho más resiliente. En la imagen que se muestra a continuación, se confirma lo descrito. 

![Texto alternativo de la imagen](imagenes/Escalabilidad4.png)

Adicionalmente, también se revisaron los resultados obtenidos de las fallas por componente, donde se aprecia que en el microservicio de órdenes, fallaron 2 solicitudes, en el de usuarios uno y en el de productos 1. Lo que muestra la resilencia del sistema, gracias a la táctica de escalado. 

![Texto alternativo de la imagen](imagenes/EscalabilidadC.png)

Entonces, dado el alto porcentaje de transacciones exitosas (99,8 %) se evidencia, la importancia de aplicar tácticas como el auto-escaling, con el fin de garantizar el correcto funcionamiento del sistema.
