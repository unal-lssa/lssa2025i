# Laboratory 5 - Architectural Verification
## 1. Objective

## 2. Architectural Overview

### a. Architecture (Lab 4)

Client → Load Balancer → API Gateway → Load Balancer → Microservice → Cache | Database

Key Features:

* The Load Balancer distributes requests across multiple API Gateway and microservices instances.
* The API Gateway routes requests to a specialized worker service for long-task.
* The API Gateway routes requests to services, supports caching and async processing.
* A Cache (e.g., in-memory dict or Redis in real-life) reduces DB access.
* Async Task Queue offloads expensive operations.

### d. Components

**load_balancer.py** – a simple round-robin reverse proxy.

**api_gateway.py** – handles request routing, caching and authentication.

**microservice.py** – handles sync and async endpoints.

**microservice-login.py** – handles sync login request.

**worker.py** – processes async jobs from a queue.

**database.py** – mocks data storage.

**cache.py** – simple in-memory cache service.


## 3. Instructions

Run the following command on root:


```bash
    python main.py
```

This command runs all system components that are defined on their own ports.

#### Access /data multiple times:

```bash
    curl -X GET http://127.0.0.1:8000/data
```

#### Trigger async job:

```bash
    curl -X POST -H "Content-Type: application/json" -d '{"task": "report"}' http://127.0.0.1:8000/longtask
```

These commands allowed us to confirm that the system is working.

## 4. Instructions to simulate request

```bash
    python .\main_simulator.py
```

### Conclusion

Adding some Performance & Scalability tactics leads to improved system performance. These tactics include:

* We introduced Load Balancing to distribute traffic.
* We reduced latency with Caching.
* We offloaded slow tasks with Asynchronous Processing.
* We introduced Limit Event Response.

Thanks to the simulator, you can verify that the system's performance is as agreed and even find possible areas for improvement.

## 5. Delivery

### 5.1. Deliverable

* Full name.
* The same excercise with the following improvement: Extend this design by adding additional resources to test load balancing patterns on the worker component by introducing the Weighted Round-Robin algorithm.

### 5.2. Submission Format

* The deliverable must be submitted via GitHub ([lssa2025i](https://github.com/unal-lssa/lssa2025i) repository).
* Steps:
  - Use the branch corresponding to your team (team1, team2, ...).
  - In the folder [laboratories/laboratory_5](), create an **X** folder (where X = your identity document number), which must include the **deliverable**:
    + README.md with the full name and steps for executing the exercise.
    + Related files to execute.

### 4.3. Delivery Deadline

Friday, May 09, 2025, before 23h59.