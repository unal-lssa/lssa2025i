## Nancy Vianeth Vera Rodriguez

### Laboratorio 3: Seguridad

Tomando como base el ejemplo dado, se agregaron nuevas funcionalidades asi:

1. Tiempo de vigencia del Token

    Una vez que se entrega el token valido a un usuario, se establece el tiempo de vigencia del token en 10 minutos. 
  
        expiration_time = datetime.utcnow() + timedelta(minutes=10)
     
    Si este tiempo expira, se controla el error mostrando que ha vencido el tiempo de vigencia del token.
    
         except jwt.ExpiredSignatureError:
              return jsonify({"message": "Token has expired!"}), 401
      
    
2. Se agregaron roles y recursos reservados para cada rol

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

    




   
