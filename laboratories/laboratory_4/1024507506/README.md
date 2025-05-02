# Laboratory 4 - Scalabilty

### ✅ Author

- **Name:** Jilkson Alejandro Pulido Cruz
- **ID:** 1024507506

## 🛡️ Objective
The objective of this lab is to demonstrate how applying *Performance and Scalability* tactics using architectural patterns such as **Load Balancing** and **Caching** can improve the system’s responsiveness and support higher loads.

## 🚀 Improvements Implemented

- ✅ **Authentication Layer**: Implemented JWT-based authentication via the API Gateway, validating tokens for all protected routes.

- ✅ **Load Balancer**: A custom Flask-based load balancer distributes incoming requests across two API Gateway instances, simulating horizontal scaling.

- ✅ **Horizontal Scalability of Microservices**:  
  The API Gateway forwards requests to the `/process` endpoint randomly to two microservice instances (`5001` and `5010`), demonstrating backend horizontal scalability.

- ✅ **Caching Layer**:  
  A lightweight in-memory caching service was introduced to reduce database load. The API Gateway first checks the cache before querying the database.

- ✅ **Async Processing**:  
  Long-running tasks are offloaded to a background worker via the `/longtask` endpoint, simulating non-blocking asynchronous job handling.

- ✅ **Observability**:  
  - `cache.py` exposes a `/metrics` endpoint reporting the number of hits, misses, current cache size, and hit rate.  
  - `worker.py` provides a `/metrics` endpoint displaying the number of processed asynchronous tasks.

- ✅ **Test Coverage & Usage Instructions**:  
  - Example `curl` requests are provided for testing `/data`, `/longtask`, and `/process`.
  - The system supports simulated load to validate balancing and caching effectiveness.


## ⚙️ How to Run the System

### 1. Install dependencies

```bash
pip install flask requests
```

### 2. Start all services (in separate terminals)

```python

python cache.py             # Port 5004
python database.py          # Port 5002
python microservice.py      # Port 5001
python microservice_2.py    # Port 5010
python worker.py            # Port 5005
python api_gateway.py       # Port 5000
python api_gateway_2.py     # Port 5003
python load_balancer.py     # Port 8000

```

### 3. 📊 Architecture Diagram (Mermaid)

``` mermaid
graph TD
    Client --> LB[Load Balancer]
    LB --> GW1[API Gateway 1]
    LB --> GW2[API Gateway 2]

    GW1 -->|/data| Cache
    GW2 -->|/data| Cache
    Cache --> DB[(Database)]

    GW1 -->|/process| MS1[Microservice 1 (5001)]
    GW1 -->|/process| MS2[Microservice 2 (5010)]
    GW2 -->|/process| MS1
    GW2 -->|/process| MS2

    GW1 -->|/longtask| Worker
    GW2 -->|/longtask| Worker

```

### 4. 📝 Summary of Work Performed

In this lab, we enhanced the original microservices architecture by implementing a scalable and observable system capable of handling increased load efficiently. The work included:
	•	🔐 Securing the system through JWT-based authentication validated at the API Gateway level.
	•	⚖️ Implementing a Load Balancer to distribute traffic across multiple API Gateway instances, simulating real-world scalability.
	•	📈 Scaling microservices horizontally by running two separate instances of the business logic microservice and balancing requests between them.
	•	🚀 Integrating a caching mechanism to avoid repeated database access and improve response times on frequently accessed data.
	•	⏱️ Offloading long-running operations to an asynchronous worker service using a background thread, improving system responsiveness.
	•	🔍 Adding observability through custom /metrics endpoints in the cache and worker components to monitor performance and behavior.
	•	🧪 Testing the complete system using authenticated curl requests and observing the impact of caching, load balancing, and asynchronous execution.