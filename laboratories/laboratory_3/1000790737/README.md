# Lab 3 - Security

Name: Carlos Santiago Sandoval Casallas

## 1. Services

1. API Gateway
2. Auth DB - Service
3. Data DB - Service
4. Transaction DB - Service
5. User DB - Service

## 2. Security Decisions

1. Limit active sessions per user.
2. Role system for endpoints.
3. Changing the role of a user deletes all tokens and invalidates them.
4. Tokens with expiration date.
5. A private network is used between the database of each microservice and the microservice.
6. A network is used between the microservices and the API gateway.

## 3. Run the application

### Pre-requisites

- Docker
- Docker Compose
- Python 3.8 or higher

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/unal-lssa/lssa2025i/tree/team2
   cd lssa2025i/laboratories/laboratory_3/1000790737
   ```

2. Build the Docker images:
   ```bash
    docker-compose build
    ```

## 4. Test the application

### 1. Generate a token

Generate a token for a user with the role "admin":
  ```bash
  curl --request POST \
    --url http://127.0.0.1:8080/login \
    --header 'content-type: application/json' \
    --data '{
    "username": "user1",
    "password": "password123"
  }'
  ```

### 2. Try accessing a protected endpoint

Access using the token generated in the previous step:
  ```bash
  curl --request GET \
    --url http://127.0.0.1:8080/transactions/user1 \
    --header 'authorization: Bearer <token>'
  ```

Try accessing a protected endpoint without a token:
  ```bash
  curl --request GET \
    --url http://127.0.0.1:8080/transactions/user1
  ```

### 3. Check the role logic

Generate a token for a user with the role "user":
  ```bash
  curl --request POST \
    --url http://127.0.0.1:8080/login \
    --header 'content-type: application/json' \
    --data '{
    "username": "user2",
    "password": "password456"
  }'
  ```

Try accessing an admin protected endpoint with the role "user":
  ```bash
  curl --request GET \
    --url http://127.0.0.1:8080/total/username/user2 \
    --header 'authorization: Bearer <token>'
  ```