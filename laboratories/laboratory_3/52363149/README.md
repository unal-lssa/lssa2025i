## Nancy Vianeth Vera Rodriguez

### Laboratorio 3: Seguridad

### Objetivo
The objective of this lab is to demonstrate how applying the Limit Exposure security tactic using the API
Gateway architectural pattern significantly reduces the system's attack surface. This is a core principle of
Secure by Design — building security into the architecture from the start.



### Security tactic 1: Time Based Access Control

Tiempo de vigencia del Token

    Una vez que se entrega el token valido a un usuario, se establece el tiempo de vigencia del token en 10 minutos. 
  
        expiration_time = datetime.utcnow() + timedelta(minutes=10)
     

Si este tiempo expira, se controla el error mostrando que ha vencido el tiempo de vigencia del token.
    
         except jwt.ExpiredSignatureError:
              return jsonify({"message": "Token has expired!"}), 401
      
### Security tactic 2: Limit Exposure

Se agregaron roles y recursos reservados para cada rol

     Se definieron dos roles: el rol de usuario y el de administrador:
      
         USERS = {
          "user2": {"password": "password123", "role": "user"},
          "admin1": {"password": "adminpass", "role": "admin"},
          }
  
  
  Se creo el microservicio admin_service.py y se limitó el acceso solo al rol admin
  
        
        @app.route("/admin", methods=["GET"])
        @token_required
        @role_required("admin")
        @limit_exposure
        def admin_data():
            return jsonify({"message": "Admin data accessed!"}), 200

    
### Ejecución

1. Para obtener el token con user:
   
            $headers = @{
            "Content-Type" = "application/json"
            }

            $body = '{"username": "user2", "password": "password123"}'

            $response = Invoke-WebRequest -Uri http://127.0.0.1:5000/login -Method Post -Headers $headers -Body $body
            
            $response.Content


2. Para obtener el token con admin

            
            $headers = @{
            "Content-Type" = "application/json"
            }

            $body = '{"admin": "admin1", "password": "adminpass"}'

            $response = Invoke-WebRequest -Uri http://127.0.0.1:5000/login -Method Post -Headers $headers -Body $body
            
            $response.Content

   
3. Para probar la restriccion por roles
   
   Permite acceder con un token obtenido por un usuario o por un admin

        Invoke-WebRequest -Uri http://127.0.0.1:5000/data -Method GET -Headers @{
            "Authorization" = "Token_Obtenido"
        }

    Servicio restringido al rol admin. Solo permite acceder con un token obtenido para admin
   
        Invoke-WebRequest -Uri http://127.0.0.1:5003/admin-tools -Method GET -Headers @{
            "Authorization" = "Token_obtenido"
        }



