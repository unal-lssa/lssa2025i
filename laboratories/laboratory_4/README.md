 Large-Scale Software Architecture
# Laboratory 4 - Scalabilty

## 1. Objective

The objective of this lab is to demonstrate how applying *Performance and Scalability* tactics using architectural patterns such as **Load Balancing** and **Caching** can improve the system’s responsiveness and support higher loads.

## 2. Architectural Overview

### a. Original Architecture (Lab 3)

Client → API Gateway → Microservice → Database

### b. Improved Scalable Architecture

Client → Load Balancer → API Gateway → Microservices (Async & Sync) → Cache + Database

Key Features:

* The Load Balancer distributes requests across multiple API Gateway instances.
* The API Gateway routes requests to services, supports caching and async processing.
* A Cache (e.g., in-memory dict or Redis in real-life) reduces DB access.
* Async Task Queue offloads expensive operations.

### c. Performance Tactics

#### What is Introduce Concurrency?
The **Introduce Concurrency** tactic consists of allowing the simultaneous execution of multiple tasks or processes, either by dividing the work between multiple threads, processes or instances. Associated architectural pattern: **Load Balancing**.

#### What is Reduce Computational Overhead?
The **Reduce Computational Overhead** tactic seeks to minimize unnecessary computational work within a system by eliminating or simplifying costly operations. Associated architectural pattern: **Caching**.

### d. Components

**load_balancer.py** – a simple round-robin reverse proxy.

**api_gateway.py** – handles request routing, caching and authentication.

**microservice.py** – handles sync and async endpoints.

**worker.py** – processes async jobs from a queue.

**database.py** – mocks data storage.

**cache.py** – simple in-memory cache service.

## 3. Instructions

### Step 1: Load Balancer

Simple reverse proxy using Flask that alternates requests between multiple API Gateway instances (simulate scale-out).

#### `load_balancer.py`

```python
from flask import Flask, request, redirect
import itertools

app = Flask(__name__)
api_gateways = itertools.cycle(["http://127.0.0.1:5000", "http://127.0.0.1:5003"])

@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    target = next(api_gateways)
    return redirect(f"{target}/{path}", code=307)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
```

### Step 2: Cache

#### `cache.py`

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
cache = {}

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    return jsonify({'value': cache.get(key)})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    cache[key] = data.get("value")
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    app.run(port=5004, debug=True)
```

### Step 3: Updated API Gateway

Add caching logic and route long operations to async queue.

#### `api_gateway.py`

```python
from flask import Flask, request, jsonify
import jwt, requests
from functools import wraps
from threading import Thread
import time

app = Flask(__name__)
SECRET_KEY = "secret"

# Decorators (reuse token auth if desired)
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token: return jsonify({'error': 'Missing token'}), 403
        try: jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except: return jsonify({'error': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return wrapper

# Cached data access
@app.route("/data", methods=["GET"])
@token_required
def get_data():
    cache_resp = requests.get("http://127.0.0.1:5004/cache/my_data").json()
    if cache_resp['value']:
        return jsonify({'cached': True, 'data': cache_resp['value']})
    # Simulate DB fetch
    db_resp = requests.get("http://127.0.0.1:5002/db").json()
    requests.post("http://127.0.0.1:5004/cache/my_data", json={'value': db_resp['message']})
    return jsonify({'cached': False, 'data': db_resp['message']})

# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    requests.post("http://127.0.0.1:5005/task", json=payload)
    return jsonify({'status': 'Task queued'}), 202

if __name__ == "__main__":
    app.run(port=5000, debug=True)
```

### Step 4: Microservice

#### `microservice.py`

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/process", methods=["GET"])
def process():
    return jsonify({'message': 'Business logic executed'}), 200

if __name__ == "__main__":
    app.run(port=5001, debug=True)
```

### Step 5: Worker

#### `worker.py`

```python
from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

@app.route("/task", methods=["POST"])
def handle_task():
    data = request.json
    thread = threading.Thread(target=process_task, args=(data,))
    thread.start()
    return jsonify({'status': 'Started'}), 202

def process_task(data):
    print(f"Processing task: {data}")
    time.sleep(5)  # Simulate delay
    print("Task complete")

if __name__ == "__main__":
    app.run(port=5005, debug=True)
```

### Step 6: Database

#### `database.py`

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/db", methods=["GET"])
def db_data():
    return jsonify({'message': 'Fetched fresh data from DB'})

if __name__ == "__main__":
    app.run(port=5002, debug=True)

```

### Step 7: Test the Architecture

#### Start all services
Run the following commands to start each service in separate terminals:

```bash
    python cache.py
    python database.py
    python microservice.py
    python worker.py
    python api_gateway.py  # Also run a second instance on port 5003 to simulate load balancing
    python load_balancer.py
```

#### Access /data multiple times:

```bash
    curl -X GET http://127.0.0.1:8000/data
```

#### Trigger async job:

```bash
    curl -X POST -H "Content-Type: application/json" -d '{"task": "report"}' http://127.0.0.1:8000/longtask
```

Check terminal logs in the worker.

### Conclusion

By adding Performance & Scalability tactics to the original secure architecture:

* We introduced Load Balancing to distribute traffic.
* We reduced latency with Caching.
* We offloaded slow tasks with Asynchronous Processing.

This setup simulates how real-world systems ensure responsiveness and elasticity under growing user demand.

## 4. Delivery

### 4.1. Deliverable

* Full name.
* The same excercise with the following improvement: expand this design by adding additional resources for testing *load balancing* and *caching* patterns.

### 4.2. Submission Format

* The deliverable must be submitted via GitHub ([lssa2025i](https://github.com/unal-lssa/lssa2025i) repository).
* Steps:
  - Use the branch corresponding to your team (team1, team2, ...).
  - In the folder [laboratories/laboratory_4](), create an **X** folder (where X = your identity document number), which must include the **deliverable**:
    + README.md with the full name and steps for executing the exercise.
    + Related files to execute.

### 4.3. Delivery Deadline

Friday, May 2, 2025, before 23h59.
