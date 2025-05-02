### Nancy Vianeth Vera R

## Laboratorio 4: Escalabilidad

### Caracteristicas del modelo y mejoras implementadas


1. Escalabilidad horizontal:
   Se agregaron nuevos microservicios: Se agregó el microservice2, y el analytics_service. De esta manera se demuestra la alta escalabilidad del modelo. Cada microservicio puede escalar de manera independiente sin afectar el modelo. Para el caso de analytics_service se trata de un nuevo microservicio que pudo ser agregado al modelo sin tener afectacion en el resto de los componentes. Para el caso de microservice2 se trata de una instancia de microservice. Esto se podría implementar en un escenario real, cuando un microservicio requiera mayores recursos, por una alta demanda, por ejemplo. 
    
2. Balanceo de carga:
   Permite distribuir la ejecución de las solicitudes, entre los diferentes microservicios que se encuentran disponibles. Si una instancia deja de responder, las otras procesan las peticiones. Así mismo, cuando existe una alta demanda, el balanceador reparte las tareas entre los microservicios disponibles. 

3. Caché local distribuida
  Se reduce la carga a la base de datos empleando almacenamiento en caché. De esta manera, es posible recuperar datos sin ir a la base de datos, lo cual mejora el performance del modelo.

4. Escalabilidad en manejo de sesiones
   Los tokens JWT permiten que la autenticación se gestione de manera descentralizada, sin necesidad de almacenar información de sesión en un servidor central. Esto significa que cualquier instancia de microservicio puede manejar la autenticación de un usuario, sin que haya un punto de falla único o sobrecarga de un servidor de sesiones. A medida que el sistema escala, no es necesario un servicio centralizado para gestionar las sesiones de los usuarios. Cada microservicio puede verificar la validez del token de manera independiente, lo que distribuye la carga.

5. Gestión asincronica de tareas
   Las tareas largas se delegan a los "workers", con lo cual éstos se podrían escalar de manera independiente. Además de esto, el sistema se proteje al impedir que las tareas largas bloqueen otros procesos.


#### Ejecución:

1. Ejecutar star_services para levantar todos los servicios


       python star_services.py


3. Obtener un token valido ejecutando user


         python user.py


4. Se pueden hacer llamados get y post a los diferentes microservicios. El load_balancer se encargará de distribuir estas peticiones entre los microservicios disponibles:


| **Componente**                    | **Puerto** | **Rutas**                                 | **Funcionalidad**                                                                                     
| --------------------------------- | ---------- | ----------------------------------------- | -----------------------------------------------------------------------------------------------------
| **api_gateway**                   | 8000       | `/data`, `/longtask`, `/db`, `/analytics` | Punto de entrada principal. Verifica el token JWT y redirige las peticiones al balanceador 
| **load_balancer**                 |            | Interno (usado por api\_gateway)          | Balancea peticiones entre `microservicio1` y `microservicio2` para `/data` y `/longtask`           
| **microservice**                  | 5001       | `/data`, `/longtask`                      | Devuelve datos simulados y redirige tareas largas al **worker**.                                      
| **microservice2**                 | 5002       | `/data`, `/longtask`                      | Similar a microservicio1.                      
| **database**                      | 5003       | `/db`                                     | Simula acceso a base de datos.                                        
| **analytics**                     | 5005       | `/analyze`                                | Simula analisis de datos.                             
| **worker**                        | 5006       | `/task`                                   | Simula ejecución de tareas asincrónicas largas                                                

   
