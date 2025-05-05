import jwt

SECRET_KEY = "secret"
payload = {"username": "user1"}

token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
print(token)
