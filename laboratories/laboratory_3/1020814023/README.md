# [LSSA_2025i] - U2 - Laboratory 3

## Full name: Juan Sebastián Alcina Rodríguez

# Additional services

1. Message microservice

This microservice return a simple message. If the request is successful it will return: 'Este microservicio únicamente devuelve este mensaje si tienes el rol "user". Consulta satisfactoria!'

2. Stats microservice

This microservice counts the total number of visits. It returns the number of visits the service has.

# New rules for limiting exposure

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
