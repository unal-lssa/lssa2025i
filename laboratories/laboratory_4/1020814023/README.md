# [LSSA_2025i] - U2 - Laboratory 3

## Full name: Juan Sebastián Alcina Rodríguez

# New configuration to test load balancing and caching patterns

1. Log de trazabilidad por instanica

Modifica api_gateway.py (y su segunda instancia en el puerto 5003) para que cada instancia imprima un identificador único (ej. print("Handled by API Gateway 1")) y así validar que el balanceador realmente distribuye las peticiones.

1. Roles and permissions

The users with the role "user" can access the "Message" microservice and the users that have the "admin" role can access the "Stats" microservice.

2. Time limitations

Requests to the "Message" and "Stats" microservices are only allowed between 1pm and 11pm.

# Steps to execute the exercise

Run the following commands to start each service in separate terminals:

1. API Gateway (Port 5000)
```
python api_gateway.py
```

2. Microservice (Port 5001)
```
python microservice.py
```

3. Database (Port 5002)
```
python database.py
```

4. Message Microservice (Port 5003)
```
python message_microservice.py
```

5. Stats Microservice (Port 5004)
```
python stats_microservice.py
```

6. Use the POST /login endpoint to log in and get a JWT token. Yo can get a token for two users, change the request accordingly:

"user1": {"password": "password123", "role": "admin"}

```
curl -X POST -H "Content-Type: application/json" -d '{"username": "user1",
"password": "password123"}' http://127.0.0.1:5000/login
```

"user2": {"password": "password123", "role": "user"}

```
curl -X POST -H "Content-Type: application/json" -d '{"username": "user2",
"password": "password123"}' http://127.0.0.1:5000/login
```

7. Use the GET request in the API gateway with the JWT token in the Authorization header to access each microservice:

Microservice

```
curl -X GET -H "Authorization: Bearer <your_token>"
http://127.0.0.1:5000/microservice
```

Database

```
curl -X GET -H "Authorization: Bearer <your_token>"
http://127.0.0.1:5000/data
```

Message Microservice

```
curl -X GET -H "Authorization: Bearer <your_token>"
http://127.0.0.1:5000/message
```

Stats Microservice

```
curl -X GET -H "Authorization: Bearer <your_token>"
http://127.0.0.1:5000/stats
```

# Notes

I didn´t contenerize the application because I was having some issues with the "Time limitations" limiting exposure rule. The time functions inside the containers were not working correctly.
