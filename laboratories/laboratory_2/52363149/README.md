**Nancy Vianeth Vera Rodiguez**

### Cambios realizados

#### En el modelo
* Se crearon 2 nuevos backend, para contar con 3 backend en total
* Se creó el componente para el balanceador de carga
* Se crearon los conectores entre el balanceador y cada uno de los backend
* Se creó un conector del frontend al balanceador
  
      architecture:
      component load_balancer lssa_lb
      component frontend lssa_fe
      component backend lssa_be1
      component backend lssa_be2
      component backend lssa_be3
      component database lssa_db
      
      connector http lssa_fe -> lssa_lb  
      connector db_connector lssa_be1 -> lssa_db  
      connector load_balancer_connector lssa_lb -> lssa_be1  
      connector load_balancer_connector lssa_lb -> lssa_be2  
      connector load_balancer_connector lssa_lb -> lssa_be3  

#### En transformaciones
* Se genera el balanceador
* Se actualizar la generacion del docker-compose para incluir el balanceador

      def generate_nginx_conf(components):
      
          path = "skeleton/lssa_lb"
          os.makedirs(path, exist_ok=True)
      
          nginx_conf = """
      events {
          worker_connections 1024;
      }
      
      http {
          upstream backend {
      """
      
          for name, ctype in components.items():
              if ctype == "backend":
                  nginx_conf += f"        server {name}:80;\n"
      
          nginx_conf += """
          }
      
          server {
              listen 80;
              
              location / {
                  proxy_pass http://backend;
                  proxy_set_header Host $host;
                  proxy_set_header X-Real-IP $remote_addr;
                  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                  proxy_set_header X-Forwarded-Proto $scheme;
              }
          }
      }
      """
  

### Pruebas

* Frontend en ejecución

  
* Consulta a la Base de Datos

  
* Validación del balanceo entre los tres backend

