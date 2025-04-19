# Lab 3
***Name:*** Juan Esteban Hunter Malaver
## 1. Description: 
This project demonstrates a **large-scale, secure microservices architecture** built with Flask, Docker, and API Gateway patterns. It enforces Security-by-Design principles to minimize attack surfaces and prevent unauthorized access.

## 2. Architecture
The system consists of the following components:
- **API Gateway**: The sole entry point for all client requests, handling authentication, rate limiting, and routing.
- **Microservices** (3):
  - `login-microservice`: Manages user authentication (JWT).
  - `products-microservice`: Handles product data.
  - `companies-microservice`: Manages company data.
- **Databases**: Each microservice has its own isolated simulated database (Data Partitioning pattern).
### Flow: Client → API Gateway (Rate Limiting) → [Microservice] → [Database]

## 3. Security-by-Design Decisions
### a. Architectural Pattern: Data Partitioning
- **Description**:  
  Data is partitioned by entity (login, products, companies), with each microservice managing its own database. This ensures:
  - **Isolation**: Compromising one microservice doesn’t affect others.
  - **Scalability**: Each service can be scaled independently.
- **Implementation**:  
  - Dedicated simulated databases for `products`, `companies`, and `login` microservices.
  - No cross-database queries; strict service boundaries.

### b. Architectural Pattern: Rate Limiting
- **Description**:  
  The API Gateway enforces request rate limits to mitigate DDoS attacks and abuse.
- **Implementation**:  
  - Flask-Limiter.
  - Endpoint-specific limits:
    - `/login`: 5 requests/minute per IP.
    - `/products`, `/companies`: 100 requests/minute per IP.
  - Responses include `429 Too Many Requests` when limits are exceeded.

### c. Strict Access Control
- **IP Whitelisting**:  
  - Only the API Gateway’s IP can access microservices.
  - Only microservices’ IPs can access their databases.
- **Network Isolation**:  
  - Docker internal networks enforce communication rules.
  - Example: `products-microservice` can’t directly call `companies-database`.

### d. Key Security Features
- **Single Entry Point**: All traffic flows through the API Gateway (enforces JWT, rate limits, and IP checks).

## 4. How to deploy
### 1. Prerequisites:
1. Docker (v24.0.0+)
2. Docker Compose (2.0.0+)
### 2. Clone the repository and this particular branch (Team2)
     git clone git@github.com:unal-lssa/lssa2025i.git 

     cd lssa_2025i

     git branch team2

     git checkout team2

     cd laboratories/laboratory_3/1000381967

     docker compose up --build

This will:

* Build images for the API Gateway, microservices, and databases.
* Start all containers in an isolated Docker network.

Check the containers

    docker ps

## 5. How to test
Go to your terminal and run next comands

### Login (Obtain jwt token)

     curl -X POST -H "Content-Type: application/json" -d '{"username": "user1", "password": "password123"}' http://127.0.0.1:5000/login

This will respond whit ur token, copy and save it, it will be useful for other petitions. It will look like this:

    {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIxIn0.b8zWC_EEAbaYmdIkEbKeNeptteAlJSKFAS223Gk"
    }

### Try acces via Api-Gateway whitouy JWT token
    curl -X GET http://localhost:5000/companies

U will obtain a message like this:

    { 
        "message": "Token is missing!" 
    }

### Acces microservices with token without using ApiGateway

    curl -X GET http://localhost:5004/products -H "Authorization: <Token>"

U will obtain a message like this:

    {
        "message": "Forbidden: Unauthorized IP"
    }
Test whit other microservices an simulated databases as u want.

### Access Microservices with jwt token and via Api-Gateway.

    curl -X GET http://localhost:5000/products -H "Authorization: <Token>"

    curl -X GET http://localhost:5000/companies -H "Authorization: <Token>"

### Test frecuency petitions limits:

    for i in {1..6}; do 
        curl -X POST \
         -H "Content-Type: application/json" \
        -d '{"username": "user1", "password": "password123"}' \
        http://127.0.0.1:5000/login
        echo ""  # Salto de línea entre respuestas
    done

    