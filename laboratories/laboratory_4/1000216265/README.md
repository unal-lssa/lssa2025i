# Laboratory 4: Scalability and Performance
### Juan Andres Orozco Velandia

This project demonstrates architectural patterns for improving system scalability and performance, focusing on load balancing and caching.

## Architecture Overview

The system consists of the following components:
- **Load Balancer**: Distributes requests between multiple API Gateway instances
- **API Gateway**: Handles authentication, routing, and caching
- **Cache Service**: Provides in-memory caching with TTL support
- **Database Service**: Simulates a database with configurable response delays
- **Microservices**: Process business logic (multiple instances)
- **Worker Service**: Handles asynchronous task processing
- **Testing Scripts**: External scripts for testing load balancing and caching patterns

## Performance & Scalability Tactics

### 1. Load Balancing
The system implements load balancing at two levels:
- **API Gateway Level**: The load balancer distributes requests across multiple API Gateway instances
- **Microservice Level**: API Gateway distributes requests across multiple microservice instances

### 2. Caching
The system includes a dedicated cache service with TTL (Time-To-Live) support to reduce database access, implementing the "Reduce Computational Overhead" tactic.

### 3. Asynchronous Processing
Long-running tasks are offloaded to a worker service that processes them asynchronously.

## Project Structure

```
├── docker-compose.yml       # Orchestrates all services
├── README.md                # Project documentation
├── src/                     # Source code
│   ├── api_gateway/         # API Gateway service
│   ├── cache/               # Cache service
│   ├── database/            # Database service
│   ├── load_balancer/       # Load Balancer service
│   ├── microservice/        # Microservice
│   └── worker/              # Async worker service
└── tests/                   # External testing scripts
    ├── load_balancing_test.py   # Load balancing tests
    ├── caching_test.py          # Caching performance tests
    ├── microservice_routing_test.py  # Microservice routing tests
    └── requirements.txt          # Test dependencies
```

## Running the Project

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for running the test scripts)

### Starting the Services
1. Clone the repository
2. Navigate to the project directory
3. Start all services:

```bash
docker-compose up --build
```

This will start all services defined in the docker-compose.yml file:
- Load Balancer (port 8000)
- API Gateway instances (ports 5000, 5003)
- Cache Service (port 5004)
- Database Service (port 5002)
- Microservice instances (ports 5001, 5006, 5007)
- Worker Service (port 5005)

### Running the Tests

1. Install the test dependencies:
```bash
cd tests
pip install -r requirements.txt
```

2. Test load balancing across API Gateway instances:
```bash
python load_balancing_test.py --requests 100 --concurrency 10
```

3. Test caching performance:
```bash
python caching_test.py --iterations 5 --requests 10
```

4. Test microservice routing:
```bash
python microservice_routing_test.py --requests 50 --concurrency 5
```

Results will be saved to the `results` directory as PNG images.

## Manual Testing

### Testing Load Balancing

1. First, obtain an authentication token:
```bash
curl -X GET http://localhost:8000/token
```

2. Make multiple requests to observe balanced routing:
```bash
curl -X GET http://localhost:8000/data -H "Authorization: <token>"
```

3. Check the distribution of requests across different API Gateway instances in the response.

### Testing Caching

1. Make an initial request to a new key (cache miss):
```bash
curl -X GET "http://localhost:8000/data?key=test_key" -H "Authorization: <token>"
```

2. Make the same request again (cache hit):
```bash
curl -X GET "http://localhost:8000/data?key=test_key" -H "Authorization: <token>"
```

3. Observe the difference in response times and the "cached: true" flag.

### Testing Microservice Load Balancing

1. Make multiple requests to the process endpoint:
```bash
curl -X GET http://localhost:8000/process -H "Authorization: <token>"
```

2. Note the service_id field in the response, which should vary between requests.

### Testing Asynchronous Processing

1. Submit a long-running task:
```bash
curl -X POST http://localhost:8000/longtask -H "Authorization: <token>" -H "Content-Type: application/json" -d '{"task":"complex_calculation"}'
```

2. Check the task status:
```bash
curl -X GET http://localhost:5005/task/0 -H "Authorization: <token>"
```

## Key Improvements Made

1. **Dockerization**: All services are containerized and orchestrated using Docker Compose.

2. **Enhanced Load Balancer**:
   - Health checking of API Gateways
   - Request distribution metrics
   - Proper request forwarding

3. **Improved Cache Service**:
   - Added TTL support
   - Cache statistics endpoint
   - Cache flush capability

4. **Microservice Scaling**:
   - Multiple microservice instances 
   - Request distribution across instances

5. **Metrics Collection**:
   - Prometheus metrics for monitoring load balancing effectiveness
   - Cache hit/miss metrics
   - Response time tracking

6. **Testing Tools**:
   - External load testing scripts
   - Visualization of results
   - Performance analysis

## Architectural Benefits

- **Horizontal Scalability**: Additional API Gateway or microservice instances can be added easily.
- **Improved Response Time**: Caching reduces database load and speeds up common requests.
- **Better Resource Utilization**: Load balancing ensures even distribution of work across instances.
- **System Resilience**: Failed components can be detected and bypassed.
