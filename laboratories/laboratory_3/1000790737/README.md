# Lab 3 - Security

Name: Carlos Santiago Sandoval Casallas

## TO-DO

- [X] Implementar DB
  - [X] Implementar estructuras de datos para simular operaciones
    - [X] Users DB
    - [X] Tokens DB
    - [X] Data DB
    - [X] Transactions DB
- [ ] Implementar servicios
  - [X] Users MS
  - [ ] Auth MS
    - [ ] Implementar logica de tokens
      - [ ] Blacklist
      - [ ] Recuento de sesiones activas por usuario
      - [ ] Trigger que si se cambian los roles de un usuario se invaliden sus tokens actuales
  - [X] Data MS
  - [X] Transaction MS
- [ ] Implementar Gateway
  - [ ] Agregar recuento sesiones activas (definir un limite)
  - [ ] Agregar invalidacion de sesion por tiempo
    - [ ] Delta de Tiempo
    - [ ] Invalidar Token
    - [ ] Cambio en los permisos de un usuario invalida sus tokens
  - [ ] Realizar el orquestamiento de las llamadas para que no se puedan hacer operaciones invalidas
- [ ] Docker
  - [ ] Implementar redes privadas
    - [ ] Entre Servicios y DBs
    - [ ] Entre API Gateway y servicios
- [ ] Implementar sistema de roles
  - [ ] Endopoints accesibles solo por determinados roles