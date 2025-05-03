## Laboratory 4
# Lucas Peña Salas
# 1019147265

## Summary of Changes

### Caching Mechanisms
- **Login Service**: Implemented a very simple login service that returns a token that should be used in the `Authorization` header of the requests. 
- **Session Caching**: Added endpoints in `cache.py` to store and retrieve session data, reducing the need for repeated database queries.
- **Authentication Caching**: Integrated token caching in `api_gateway.py` to minimize the overhead of decoding and verifying tokens repeatedly.

### Load Balancing Patterns
- **Round Robin**: Implemented a round-robin load balancing strategy in `load_balancer.py` to distribute requests evenly across API gateways.
- **Random Balancing**: Added a random load balancing strategy to distribute requests randomly among available API gateways.
- **Weighted Round Robin**: Introduced a weighted round-robin strategy to prioritize certain API gateways by assigning them higher weights.

### How to test

## Testing Instructions

### Step 1: Start the Services
1. Open a terminal and navigate to the `laboratories/laboratory_4/1019147265` directory.
2. Start the login service by running the following command:
   ```bash
   docker-compose up --build
   ```

### Step 2: Obtain an Authorization Token
1. Use the following `curl` command to log in to the login service and obtain an authorization token:
   ```bash
   curl -X GET http://localhost:5006/login -H "Content-Type: application/json"
   ```
2. Copy the `Authorization` token from the response.

### Step 3: Test Load Balancing Endpoints

#### Round Robin Endpoint
1. Use the following `curl` command to send a request to the round-robin endpoint:
   ```bash
   curl -X GET http://localhost:8000/round_robin/data -H "Authorization: <your_token>"
   ```
2. Repeat the command multiple times to observe the requests being distributed across API gateways.

#### Random Balancer Endpoint
1. Use the following `curl` command to send a request to the random balancer endpoint:
   ```bash
   curl -X GET http://localhost:8000/random/data -H "Authorization: <your_token>"
   ```
2. Repeat the command multiple times to observe the requests being distributed randomly across API gateways.

#### Weighted Round Robin Endpoint
1. Use the following `curl` command to send a request to the weighted round-robin endpoint:
   ```bash
   curl -X GET http://localhost:8000/weighted_round_robin/data -H "Authorization: <your_token>"
   ```
2. Repeat the command multiple times to observe the requests being distributed with priority to the higher-weighted API gateway.



