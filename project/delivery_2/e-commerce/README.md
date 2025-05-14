# Arquitectura distribuida basada en microservicios para un E-commerce 

#### Sergio Andrés Cabezas
#### Jilkson Alejandro Pulido Cruz
#### Diego Alejandro Rodriguez Martinez
#### Yosman Alexis Arenas Jimenez
#### Juan David Ramírez Ávila

El objetivo principal de esta segunda entrega es realizar un proceso iterativo de diseño parcial y verificación de la arquitectura de distribuida basada en microservicios para un E-commerce, mediante un enfoque práctico y estructurado que permita evaluar atributos de calidad clave como la seguridad y la escalabilidad.

---

## 1. Visión general
La arquitectura propuesta para el sistema de e-commerce se basa en principios de **microservicios desacoplados**, altamente escalables y seguros. El diseño permite gestionar de manera independiente cada dominio de negocio: usuarios, pedidos, productos, inventario y pagos, con comunicación eficiente a través de protocolos adecuados, como HTTP para interacciones tradicionales y MQTT para los eventos relacionados con el servicio de pagos.

El flujo completo desde el cliente hasta el procesamiento de pagos se maneja de forma **modular**, mejorando la resiliencia, seguridad, escalabilidad y mantenibilidad del sistema.

---

## 2. Componentes principales

A continuación, se presenta un diagrama de arquitectura de componentes y conectores. En la que se incluyo una replica del micro-servicios de usuarios, en relación a la arquitectura, que se expuso en la primera entrega del proyecto. 

La replicación del microservicio de usuarios para la arquitectura del e-commerce se hizo con el fin de garantizar la escalabilidad, permitiendo atender múltiples solicitudes concurrentes; alta disponibilidad, asegurando continuidad del servicio ante fallos; y mejor rendimiento, reduciendo la latencia en operaciones críticas como el inicio de sesión. Además, permite realizar mantenimientos sin interrupciones y adaptarse dinámicamente a la carga, mejorando la experiencia del usuario y la resiliencia del sistema.

![Texto alternativo de la imagen](Arquitectura.png)
