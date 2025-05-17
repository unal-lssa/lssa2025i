Yosman Alexis Arenas Jimenez

# Laboratory 4 - Scalabilty

## Objective

The objective of this lab is to demonstrate how applying _Performance and Scalability_ tactics using architectural patterns such as **Load Balancing** and **Caching** can improve the system’s responsiveness and support higher loads.

## Content

- **load_balancer.py**: Load balancer round-robin with _health checks_.
- **api_gateway.py**: Gateway with cache (TTL, metrics) and routing and services.
- **cache.py**: Cache on memory with TTL and automatic cleaning.
- **microservice.py**: Synchronous business service.
- **worker.py**: Worker for asynchronous tasks.
- **database.py**: Database Mock.
- **load_test.py**: Concurrent Load Test Script.
- **docker-compose.yml**: Orchestration of all services.

## Improvements Implemented

1. **Health Checks in Load Balancer**
   The load balancer checks the `/health` of each instance and skips downed instances.

2. **Automated Load Testing**
   `load_test.py` simulates multiple concurrent clients and reports success, failure, and average latency.

3. **Cache with TTL y Cleaning**

   - Each entry expires after a configurable time (default 30s).
   - A background thread deletes expired entries.

4. **Performance metrics**
   Endpoint `/metrics` in `api_gateway.py` that expose:

   - `cache_hits` and `cache_misses`
   - Average access latency to `/data`

5. **Orchestration with Docker Compose**
   Simplify the deployment of all services with a single command.

## How Run

1. **No Docker:**

   ```bash
   python cache.py         # Port 5004
   python database.py      # Port 5002
   python microservice.py  # Port 5001
   python worker.py        # Port 5005
   python api_gateway.py   # Port 5000
   python api_gateway.py   # Second gateway en Port 5003
   python load_balancer.py # Port 8000
   ```

2. **With Docker Compose:**

   ```bash
   docker-compose up --build
   ```

## Testing

- **Data/Cache:**
  Access `http://127.0.0.1:8000/data` multiple times and observe cache_hits/misses in `/metrics`.

- **Asynchronous Tasks:**

  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"task": "report"}' http://127.0.0.1:8000/longtask
  ```

  Revisa logs del worker.

- **Load:**

  ```bash
  python load_test.py
  ```
