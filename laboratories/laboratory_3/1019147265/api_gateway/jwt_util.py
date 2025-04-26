import jwt

SECRET = 'SECRET_KEY'

def verify_jwt(token):
    return jwt.decode(token, SECRET, algorithms=["HS256"])

def generate_jwt(payload):
    return jwt.encode(payload, SECRET, algorithm="HS256")