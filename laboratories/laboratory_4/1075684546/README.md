# [LSSA_2025i] - U2 - Laboratory 4 - Large Scale System Architecture

## Full name: José Fabián García Camargo

## Code Updates

### 1. Load Balancer
- Implementation of an intelligent load balancer that:
  - Monitors API Gateway health in real-time
  - Uses a latency-based selection algorithm
  - Handles multiple HTTP methods (GET, POST, PUT, DELETE, PATCH, OPTIONS)
  - Implements a health monitoring system with separate threads
  - Maintains latency statistics for each gateway

### 2. API Gateway
- Implementation of multiple API Gateways (5 instances) that:
  - Distribute load across different ports (5000, 5006, 5007, 5008, 5009)
  - Provide health endpoints for monitoring
  - Handle request routing to microservices

### 3. Microservices
- Distributed architecture with:
  - Independent and decoupled services
  - REST API communication
  - Independent state management
  - Horizontal scalability

### 4. Cache System
- Implementation of a cache layer that:
  - Improves system performance
  - Reduces database load
  - Implements cache invalidation strategies

### 5. Database
- Data persistence system that:
  - Efficiently stores information
  - Provides concurrent access
  - Implements backup and recovery mechanisms

### 6. Workers
- Asynchronous processing system that:
  - Handles background tasks
  - Processes heavy operations without blocking the main system
  - Implements work queues

## Performance Improvements
- Implementation of latency-based load balancing
- Cache system to reduce response times
- Asynchronous processing of heavy tasks
- Continuous system health monitoring

## Security
- Request validation in API Gateways
- Secure handling of sensitive data
- Implementation of timeouts and circuit breakers

## Monitoring
- Distributed logging system
- Health endpoints for each component
- Latency and availability metrics

## Scalability
- Horizontally scalable architecture
- Dynamic load balancing
- Independent and decoupled services

## Project Structure
```
laboratory_4/
├── api_gateway/      # Multiple API Gateway instances
├── load_balancer/    # Intelligent load balancer
├── microservice/     # Application microservices
├── cache/           # Cache system
├── database/        # Database
├── worker/          # Asynchronous processing system
└── docker-compose.yml # Container configuration
``` 