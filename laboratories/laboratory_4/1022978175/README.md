# Enhanced Scalability Architecture Lab

This project expands the original architecture from Laboratory 4 with additional resources for testing **load balancing** and **caching** patterns more effectively.

## Full Name: Sergio Andres Cabezas

## Architecture Overview

The enhanced architecture builds upon the original design with:

1. **Advanced Load Balancing**
   - Multiple load balancing algorithms (Round Robin, Weighted, Least Connections)
   - Health checks for API Gateway instances
   - Performance metrics collection

2. **Enhanced Caching Mechanisms**
   - TTL (Time-To-Live) support
   - Multi-level caching with different retention strategies
   - Cache invalidation mechanisms

3. **Improved Async Processing**
   - Priority-based task queues
   - Parallel processing with multiple workers

## Components

Here's a brief overview of the components in this enhanced architecture:

### Load Balancing Components
- `load_balancer.py`: Implements multiple load balancing strategies with health checks

### Caching Components
- `cache.py`: Basic cache with TTL and statistics
- `multi_level_cache.py`: Implements a multi-level cache with different TTLs and promotion strategies

### API Gateway and Services
- `api_gateway.py`: Improved API Gateway with caching controls and metrics
- `worker.py`: Priority-based task processing with statistics

## Setup and Execution Instructions

### Prerequisites
- Python 3.7+ installed
- Required packages: Flask, requests, matplotlib, numpy, tqdm

Install dependencies:
```bash
pip install Flask requests tqdm
```

### Step 1: Start the Services

Open separate terminal windows for each service:

```bash
# Terminal 1: Start the cache service 
# Choose either the basic or multi-level cache
python cache.py
# or
python multi_level_cache.py

# Terminal 2: Start the database mock
python database.py

# Terminal 3: Start the microservice
python microservice.py

# Terminal 4: Start the enhanced worker
python worker.py

# Terminals 5-7: Start multiple API Gateway instances
python api_gateway.py  # Default port 5000
# In a new terminal
python api_gateway.py --port=5003
# In a new terminal
python api_gateway.py --port=5006

# Terminal 8: Start the load balancer
python load_balancer.py
```

### Step 2: Manual Testing

You can also test the system manually with curl commands:

```bash
# Test with different load balancing strategies
curl -X GET "http://127.0.0.1:8000/data?strategy=round_robin" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.ZRrHA1JJJW8opsbCGfG_HACGpVUMN_a9IV7pAx_Zmeo"
curl -X GET "http://127.0.0.1:8000/data?strategy=weighted" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.ZRrHA1JJJW8opsbCGfG_HACGpVUMN_a9IV7pAx_Zmeo"
curl -X GET "http://127.0.0.1:8000/data?strategy=least_connections" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.ZRrHA1JJJW8opsbCGfG_HACGpVUMN_a9IV7pAx_Zmeo"

# Test with different cache settings
curl -X GET "http://127.0.0.1:8000/data?bypass_cache=true" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.ZRrHA1JJJW8opsbCGfG_HACGpVUMN_a9IV7pAx_Zmeo"
curl -X GET "http://127.0.0.1:8000/data?cache_ttl=60" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.ZRrHA1JJJW8opsbCGfG_HACGpVUMN_a9IV7pAx_Zmeo"

# Test complex data endpoint
curl -X GET "http://127.0.0.1:8000/data/complex?id=1" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.ZRrHA1JJJW8opsbCGfG_HACGpVUMN_a9IV7pAx_Zmeo"

# Invalidate cache key
curl -X POST "http://127.0.0.1:8000/cache/invalidate" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.ZRrHA1JJJW8opsbCGfG_HACGpVUMN_a9IV7pAx_Zmeo" -H "Content-Type: application/json" -d '{"key":"my_data"}'

# Queue task with priority
curl -X POST "http://127.0.0.1:8000/longtask?priority=high" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.ZRrHA1JJJW8opsbCGfG_HACGpVUMN_a9IV7pAx_Zmeo" -H "Content-Type: application/json" -d '{"task_type":"cpu_intensive", "duration":3}'

# Check worker stats
curl -X GET "http://127.0.0.1:5005/stats"
```

## Architecture Details

### Load Balancing Improvements

1. **Multiple Load Balancing Algorithms**
   - **Round Robin**: Simple alternating distribution
   - **Weighted Round Robin**: Distribution based on server capacity
   - **Least Connections**: Distribution to least busy server

2. **Health Checks**
   - Automatic detection of unavailable API Gateway instances
   - Removal of unhealthy instances from the rotation

### Caching Improvements

1. **TTL Support**
   - Configurable expiration times for cached items
   - Automatic purging of expired items

2. **Multi-Level Caching**
   - L1: Small, short-lived cache for frequently accessed items
   - L2: Medium-sized cache with moderate TTL
   - L3: Large cache with longer TTL
   - Promotion between levels based on access patterns

### Async Processing Improvements

1. **Priority Queues**
   - High, normal, and low priority task queues
   - Preferential processing for critical tasks

2. **Worker Pool**
   - Multiple parallel workers
   - Adjustable concurrency

## Performance Tactics Applied

### 1. Introduce Concurrency

- **Multiple API Gateway Instances**: Horizontal scaling of gateway services
- **Parallel Task Processing**: Multiple worker threads handling async tasks
- **Connection Pooling**: Managing multiple simultaneous connections

### 2. Reduce Computational Overhead

- **Multi-Level Caching**: Tiered approach to data storage
- **TTL-Based Expiration**: Avoiding stale data without manual invalidation
- **Selective Caching**: Different strategies for different data types

### 3. Manage Resources

- **Priority-Based Processing**: Ensuring critical tasks complete first
- **Load-Based Distribution**: Sending requests to less busy servers
- **Health-Based Routing**: Avoiding failed or slow instances

## Conclusion

This enhanced architecture demonstrates advanced load balancing and caching strategies that significantly improve system scalability. The implementation allows for:

1. **Better distribution of traffic** across multiple API Gateways
2. **More efficient data access** through multi-level caching with TTL
3. **Improved resource utilization** with priority-based task processing

These enhancements show how the Performance and Scalability tactics can be applied in a practical architecture to achieve better response times and handle higher load.