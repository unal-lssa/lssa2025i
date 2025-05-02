import jwt
import datetime

# Clave secreta que usas en tu aplicación (la misma en tu microservicio)
SECRET_KEY = "secret"

# Payload (datos del usuario, por ejemplo)
payload = {
    "user": "demo_revalidado",  # Aquí puedes poner cualquier dato que desees
    "exp": datetime.datetime.utcnow()
    + datetime.timedelta(hours=1),  # Tiempo de expiración del token (1 hora)
}

# Generación del token JWT
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

print("Token generado:", token)
