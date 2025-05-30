## 1. Architectural Overview

### a. Architecture (Lab 5)

Client → Load Balancer → API Gateway → Load Balancer → Microservice → Cache | Database

Key Features:

* The Load Balancer distributes requests across multiple API Gateway and microservices instances.
* The API Gateway routes requests to a specialized worker service for long-task.
* The API Gateway routes requests to services, supports caching and async processing.
* A Cache (e.g., in-memory dict or Redis in real-life) reduces DB access.
* Async Task Queue offloads expensive operations.

### b. Prerequisites

Make sure you install all the prerequisites for this lab to run correctly.
- Flask
- Request
- Matplotlib

```bash
    pip install flask requests matplotlib
```

### c. Components

**load_balancer.py** – a simple round-robin reverse proxy.

**load_balancer_ms.py** – a simple round-robin reverse proxy.

**api_gateway.py** – handles request routing, caching and authentication.

**microservice.py** – handles sync and async endpoints.

**login_microservice.py** – handles sync login request.

**worker.py** – processes async jobs from a queue.

**database.py** – mocks data storage.

**cache.py** – simple in-memory cache service.

As a result of this project we expect to have the following file structure:

```
lab5/
│
├── Components/
│   ├── cache.py
│   └── database.py
│   └── load_balancer.py
│   └── load_balancer_ms.py
│   └── login_microservice.py
│   └── microservice.py
│   └── status_tracker.py
│   └── worker.py
├── simulator/
│   ├── simulator.py
│   ├── repot_generator.py
│   └── status_log.json  # is generated when simulating
│
├── main.py
├── main_simulator.py
└──config.py
```

## 2. Instructions

### 2.1 Folders structure

Create a /Components and a /simulator folder so that you have the following structure:

```
lab5/
│
├── Components/
├── simulator/
```

### 2.2 Components

Inside the Components/ folder created in the previous step, create the following files:

#### `load_balancer.py`

```python
import itertools
from functools import wraps
from flask import Flask, jsonify, redirect
import time
import threading
import os
from Components.status_tracker import register_status

SERVICE_NAME = "LOADBALANCER_MS"
app = Flask(__name__)
microservices = itertools.cycle(["http://127.0.0.1:5001", "http://127.0.0.1:5006"])

request_timestamps = []
rate_lock = threading.Lock()

# Decorador para rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))

        now = time.time()
        with rate_lock:
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("Load Balancer MS: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Load Balancer MS': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route("/<path:path>", methods=["GET", "POST"])
@rate_limited
def forward(path):
    target = next(microservices)
    return redirect(f"{target}/{path}", code=307)

if __name__ == "__main__":
    app.run(port=8001, debug=True)
```
#### `api_gateway.py`

```python
from flask import Flask, request, jsonify
import requests
from functools import wraps
from Components.status_tracker import register_status
app = Flask(__name__)
SECRET_KEY = "secret"
SERVICE_NAME = "APIGATEWAY"
USERS = {
    "user1": "password123"
}


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'error': 'Missing or invalid token 11'}), 403

        token = auth_header.split(" ")[1]
        response = requests.post("http://127.0.0.1:5009/validate_token", json={"token": token})

        if response.status_code != 200:
            return jsonify({'error': 'Invalid or expired token'}), 403

        return f(*args, **kwargs)

    return wrapper


# Cached data access
@app.route("/data", methods=["GET"])
@token_required
def get_data():
    response = requests.get("http://127.0.0.1:8001/data")
    register_status(SERVICE_NAME, response.status_code)
    return jsonify(response.json()), response.status_code

# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    requests.post("http://127.0.0.1:5005/task", json=payload)
    register_status(SERVICE_NAME, 202)
    return jsonify({'status': 'Task queued'}), 202


# Route for user login (returns JWT token)
@app.route('/login', methods=['POST'])
def login():
    payload = request.json
    response = requests.post("http://127.0.0.1:5009/login", json=payload)
    register_status(SERVICE_NAME, response.status_code)
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(port=5000, debug=True)
```


### `cache.py`

```python
from functools import wraps
from flask import Flask, request, jsonify
import jwt, time
import threading
import os
from Components.status_tracker import register_status

SERVICE_NAME = "CACHE"
app = Flask(__name__)
cache = {}
request_timestamps = []
rate_lock = threading.Lock()

# Decorador para rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))

        now = time.time()
        with rate_lock:
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("Error Cache :Too many requests, exiting")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Error Cache': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route("/cache/<key>", methods=["GET"])
@rate_limited
def get_cache(key):
    register_status(SERVICE_NAME, 200)
    return jsonify({'value': cache.get(key)}), 200

@app.route("/cache/<key>", methods=["POST"])
@rate_limited
def set_cache(key):
    data = request.json
    cache[key] = data.get("value")
    register_status(SERVICE_NAME, 200)
    return jsonify({'status': 'ok'}), 200

if __name__ == "__main__":
    app.run(port=5004, debug=True)
```

### `database.py`

```python
from functools import wraps
from flask import Flask, jsonify
import time
import threading
import os
from Components.status_tracker import register_status

SERVICE_NAME = "DATABASE"
app = Flask(__name__)
request_timestamps = []
rate_lock = threading.Lock()

# Decorador para rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))

        now = time.time()
        with rate_lock:
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("Database error: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Database Error': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function
@app.route("/db", methods=["GET"])
@rate_limited
def db_data():
    register_status(SERVICE_NAME, 200)
    return jsonify({'message': 'Fetched fresh data from DB'})

if __name__ == "__main__":
    app.run(port=5002, debug=True)

```

### `load_balancer.py`
This load balancer is responsible for balancing the load between two API Gateway:

```python
from flask import Flask, jsonify, request, Response
import itertools
from functools import wraps
import threading
import time
import os
import requests
from Components.status_tracker import register_status

SERVICE_NAME = "LOADBALANCER_AG"

app = Flask(__name__)

api_gateways = itertools.cycle(["http://127.0.0.1:5000", "http://127.0.0.1:5003"])
request_timestamps = []
rate_lock = threading.Lock()

# Decorador para rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))

        now = time.time()
        with rate_lock:
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("AG Load Balancer: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'AG Load Balancer': 'Too many login attempts, try again later'}), 429
            else:
                register_status(SERVICE_NAME, 200)
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route("/<path:path>", methods=["GET", "POST"])
@rate_limited
def forward(path):
    target = next(api_gateways)
    url = f"{target}/{path}"

    # Reenviamos headers excepto 'Host'
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}

    # Reenvía la petición original al destino
    response = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    # Devolvemos la respuesta original
    return Response(response.content, status=response.status_code, headers=dict(response.headers))

if __name__ == "__main__":
    app.run(port=8000, debug=True)

```
### `load_balancer_ms.py`

This load balancer is responsible for balancing the load between two microservices:

```python
import itertools
from functools import wraps
from flask import Flask, jsonify, redirect
import time
import threading
import os
from Components.status_tracker import register_status

SERVICE_NAME = "LOADBALANCER_MS"
app = Flask(__name__)
microservices = itertools.cycle(["http://127.0.0.1:5001", "http://127.0.0.1:5006"])

request_timestamps = []
rate_lock = threading.Lock()

# Decorador para rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))

        now = time.time()
        with rate_lock:
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("Load Balancer MS: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Load Balancer MS': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route("/<path:path>", methods=["GET", "POST"])
@rate_limited
def forward(path):
    target = next(microservices)
    return redirect(f"{target}/{path}", code=307)

if __name__ == "__main__":
    app.run(port=8001, debug=True)
```

### `login_microservice.py`

This component abstracts all responsibilities related to token management within the system, both its creation and validation:

```python
from functools import wraps
from flask import Flask, request, jsonify
import jwt, time
import threading
import os
from Components.status_tracker import register_status
app = Flask(__name__)
SECRET_KEY = "secret"
SERVICE_NAME = "LOGIN_MS"
USERS = {
    "user1": "password123"
}

request_timestamps = []
rate_lock = threading.Lock()

# Decorador para rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))

        now = time.time()
        with rate_lock:
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("Microservice Login error: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Microservice Login error': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route('/validate_token', methods=['POST'])
def validate_token():
    token = request.json.get('token')
    if not token:
        register_status(SERVICE_NAME, 400)
        return jsonify({'error': 'Token is missing'}), 400

    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        register_status(SERVICE_NAME, 200)
        return jsonify({'valid': True}), 200
    except jwt.ExpiredSignatureError:
        register_status(SERVICE_NAME, 403)
        return jsonify({'error': 'Token expired'}), 403
    except jwt.InvalidTokenError:
        register_status(SERVICE_NAME, 403)
        return jsonify({'error': 'Invalid token'}), 403

@app.route('/login', methods=['POST'])
@rate_limited
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')

    if USERS.get(username) == password:
        token = jwt.encode({'username': username}, SECRET_KEY, algorithm="HS256")
        register_status(SERVICE_NAME, 200)
        return jsonify({'token': token})
    register_status(SERVICE_NAME, 401)
    return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == "__main__":
    app.run(port=5009, debug=True)

```

### `microservice.py`

```python
from flask import Flask, jsonify
import requests
import os
import time
import threading
from functools import wraps
from Components.status_tracker import register_status

SERVICE_NAME = "MICROSERVICE"
app = Flask(__name__)

# Variables compartidas para rate limiting
request_timestamps = []
rate_lock = threading.Lock()

# Decorador para aplicar rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))
        now = time.time()
        with rate_lock:
            # Eliminar timestamps antiguos
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("Microservice error': 'Too many requests, try again later")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Microservice error': 'Too many requests, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route("/process", methods=["GET"])
@rate_limited
def process():
    return jsonify({'message': 'Business logic executed'}), 200


@app.route("/data", methods=["GET"])
@rate_limited
def get_data():
    try:
        cache_resp = requests.get("http://127.0.0.1:5004/cache/my_data").json()
        if cache_resp['value']:
            register_status(SERVICE_NAME, 200)
            return jsonify({'cached': True, 'data': cache_resp['value']}), 200

        db_resp = requests.get("http://127.0.0.1:5002/db").json()
        requests.post("http://127.0.0.1:5004/cache/my_data", json={'value': db_resp['message']})
        return jsonify({'cached': False, 'data': db_resp['message']})
    except Exception as e:
        register_status(SERVICE_NAME, 500)
        return jsonify({'error': 'Failed to retrieve data', 'details': str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)

```
### `status_tracker.py`

This code contains utility functions to monitor the response states of each of the system components from where it is called to later be used to generate reports:

```python
import json
import threading
from pathlib import Path

# Make sure the simulator folder exists
SIMULATOR_DIR = Path(__file__).resolve().parent.parent / "simulator"
SIMULATOR_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = SIMULATOR_DIR / "status_log.json"
log_lock = threading.Lock()

def load_log():
    if not LOG_FILE.exists():
        return {}
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

def register_status(service_name, code):
    with log_lock:
        log = load_log()
        if service_name not in log:
            log[service_name] = {}
        code_str = str(code)
        log[service_name][code_str] = log[service_name].get(code_str, 0) + 1
        save_log(log)

def reset_log():
    """Deletes all records leaving the JSON clean."""
    with log_lock:
        save_log({})
```

### `worker.py`

```python
from flask import Flask, request, jsonify
import threading
import time
import os
from Components.status_tracker import register_status
from functools import wraps

SERVICE_NAME = "WORKER"

request_timestamps = []
rate_lock = threading.Lock()
app = Flask(__name__)

def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps
        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))
        now = time.time()
        with rate_lock:
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("Worker Login error: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Worker Login error': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)
        return f(*args, **kwargs)
    return decorated_function

@app.route("/task", methods=["POST"])
@rate_limited
def handle_task():
    data = request.json
    thread = threading.Thread(target=process_task, args=(data,))
    thread.start()
    register_status(SERVICE_NAME, 202)
    return jsonify({'status': 'Started'}), 202

def process_task(data):
    print(f"Processing task: {data}")
    time.sleep(5)  # Simulate delay
    print("Task complete")

if __name__ == "__main__":
    app.run(port=5005, debug=True)
```

### 2.3 Compilation elements

Create the following files in the root folder, hoping to have the following structure:

```
lab5/
│
├── Components/
│   ├── ....
├── main.py
└── config.py
```
This system has the ability to configure the different capabilities of the system and its individual components. Create the following elements to compile the complete project:

### `config.py`

This configuration file contains the values ​​that can be configured to manage the rate-limit of each of the system components:

``` python
RATE_LIMIT_CONFIG = {
    "login": {
        "MAX_REQUESTS_PER_TIME": 100,
        "RATE_LIMIT_TIME": 60
    },
    "cache": {
        "MAX_REQUESTS_PER_TIME": 10000,
        "RATE_LIMIT_TIME": 30
    },
    "db": {
        "MAX_REQUESTS_PER_TIME": 150,
        "RATE_LIMIT_TIME": 60
    },
    "microservice_A": {
        "MAX_REQUESTS_PER_TIME": 1000,
        "RATE_LIMIT_TIME": 60
    },
    "microservice_B": {
        "MAX_REQUESTS_PER_TIME": 50,
        "RATE_LIMIT_TIME": 60
    },
    "worker": {
        "MAX_REQUESTS_PER_TIME": 200,
        "RATE_LIMIT_TIME": 60
    },
    "gateway": {
        "MAX_REQUESTS_PER_TIME": 120,
        "RATE_LIMIT_TIME": 60
    },
    "load_balancer": {
        "MAX_REQUESTS_PER_TIME": 10000,
        "RATE_LIMIT_TIME": 60
    }
}
```
### `main.py`

This main class aims to compile all the components necessary for the system to function and add individual capabilities:

```python
import multiprocessing
import os
from Components import api_gateway, cache, database, load_balancer_ms, login_microservice, microservice, worker, \
    load_balancer
import config

def apply_rate_limit_config(service_name):
    cfg = config.RATE_LIMIT_CONFIG[service_name]
    os.environ["MAX_REQUESTS_PER_TIME"] = str(cfg["MAX_REQUESTS_PER_TIME"])
    os.environ["RATE_LIMIT_TIME"] = str(cfg["RATE_LIMIT_TIME"])


def run_login_microservice(port):
    apply_rate_limit_config("login")
    login_microservice.app.run(port=port, debug=False, use_reloader=False)

def run_cache_service(port):
    apply_rate_limit_config("cache")
    cache.app.run(port=port, debug=False, use_reloader=False)

def run_db_service(port):
    apply_rate_limit_config("db")
    database.app.run(port=port, debug=False, use_reloader=False)

def run_microservice_B(port):
    apply_rate_limit_config("microservice_B")
    microservice.app.run(port=port, debug=False, use_reloader=False)

def run_microservice_A(port):
    apply_rate_limit_config("microservice_A")
    microservice.app.run(port=port, debug=False, use_reloader=False)

def run_worker(port):
    apply_rate_limit_config("worker")
    worker.app.run(port=port, debug=False, use_reloader=False)

def run_app_service(port):
    apply_rate_limit_config("gateway")
    api_gateway.app.run(port=port, debug=False, use_reloader=False)

def run_load_balancer(port):
    apply_rate_limit_config("load_balancer")
    load_balancer.app.run(port=port, debug=False, use_reloader=False)


def run_load_balancer_ms(port):
    apply_rate_limit_config("load_balancer")
    load_balancer_ms.app.run(port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    multiprocessing.freeze_support()

    processes = [
        multiprocessing.Process(target=run_login_microservice, args=(5009,)),
        multiprocessing.Process(target=run_cache_service, args=(5004,)),
        multiprocessing.Process(target=run_db_service, args=(5002,)),
        multiprocessing.Process(target=run_microservice_A, args=(5001,)),
        multiprocessing.Process(target=run_microservice_B, args=(5006,)),
        multiprocessing.Process(target=run_worker, args=(5005,)),
        multiprocessing.Process(target=run_app_service, args=(5000,)),
        multiprocessing.Process(target=run_app_service, args=(5003,)),
        multiprocessing.Process(target=run_load_balancer, args=(8000,)),
        multiprocessing.Process(target=run_load_balancer_ms, args=(8001,))
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

```

## 2.3 Run the system

Run the following command to compile all components from main.py

```bash
    python main.py
```
To confirm that the system is working completely fine you can run the following commands:

#### Access /data multiple times:

```bash
    curl -X GET http://127.0.0.1:8000/data
```

#### Trigger async job:

```bash
    curl -X POST -H "Content-Type: application/json" -d '{"task": "report"}' http://127.0.0.1:8000/longtask
```

These commands allowed us to confirm that the system is working.

## 3. Instructions to simulate request

Now to create the simulations and validation of the system, the following files must be created in the previously created simulator folder:

```
lab5/
│
├── Components/
│   ├── ...
├── simulator/
│   ├── simulator.py
│   ├── repot_generator.py
│   └── status_log.json  # is generated when simulating
│
├── main_simulator.py
```

### `simulator.py`

This file contains the instructions needed to send a group of transactions to the different endpoints of the software system, in this case 300 /data requests and 300 /longtask requests:

```python
import requests
from Components.status_tracker import reset_log
data = {
    "username": "user1",
    "password": "password123"
}

main_loadbalancer = "http://127.0.0.1:8000"

def request_login():
    url = f"{main_loadbalancer}/login"
    headers = {"Content-Type": "application/json"}
    data = {
        "username": "user1",
        "password": "password123"
    }

    response = requests.post(url, json=data, headers=headers)
    data = response.json()
    returned_token = data.get("token")
    return returned_token

def request_data(token):
    url = f"{main_loadbalancer}/data"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def request_long_task(token):
    url = f"{main_loadbalancer}/longtask"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    body = {
        "task": "report"
    }
    response = requests.post(url, headers=headers, json=body)

    return response.json()



def run_simulation(token, purchase_count=300):


    print('-----------------Start requesting data-----------------')
    for i in range(1, purchase_count + 1):
        request_data(token)
    print('-----------------Start requesting longtask-----------------')
    for i in range(1, purchase_count + 1):
        request_long_task(token)

def main():
    reset_log()
    token = request_login()
    run_simulation(token)


```

### `report_generator.py`

This file contains the instructions needed to create a PDF report with the simulation results:

```python
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime


def generate_status_report_pdf(json_path, pdf_dir="."):
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"status_report_{timestamp}.pdf"
    pdf_path = f"{pdf_dir}/{pdf_filename}"

    # Load data
    with open(json_path, "r") as f:
        data = json.load(f)

    # Initialize PDF
    with PdfPages(pdf_path) as pdf:
        # 1. Total requests per service graph
        total_requests = {
            service: sum(map(int, codes.values()))
            for service, codes in data.items()
        }

        plt.figure(figsize=(8, 6))
        plt.bar(total_requests.keys(), total_requests.values(), color='skyblue')
        plt.title("Total Requests per Service")
        plt.ylabel("Number of Requests")
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # 2. Status codes per service graph
        for service, codes in data.items():
            plt.figure(figsize=(6, 4))
            codes_sorted = dict(sorted(codes.items()))
            codes_list = list(codes_sorted.keys())
            counts = [int(v) for v in codes_sorted.values()]

            # Asignar color rojo si no está en el rango 200–299
            colors = [
                'lightgreen' if 200 <= int(code) < 300 else 'red'
                for code in codes_list
            ]

            plt.bar(codes_list, counts, color=colors)
            plt.title(f"Status Codes in {service}")
            plt.xlabel("HTTP Code")
            plt.ylabel("Count")
            plt.tight_layout()
            pdf.savefig()
            plt.close()

        # 3. Textual report (two columns)
        report_text = []
        report_text.append("Status Report Summary:\n")

        for service, codes in data.items():
            total_requests_service = sum(map(int, codes.values()))
            report_text.append(f"\nService: {service}")
            report_text.append(f"Total Requests: {total_requests_service}")
            for code, count in codes.items():
                report_text.append(f"  Code {code}: {count} requests")

        # Add the report in two columns
        fig, ax = plt.subplots(figsize=(8, 11))
        ax.axis('off')

        # Split the text into two roughly equal parts
        midpoint = len(report_text) // 2
        left_text = "\n".join(report_text[:midpoint])
        right_text = "\n".join(report_text[midpoint:])

        # Place the two columns of text
        ax.text(0.05, 0.95, left_text, fontsize=10, ha='left', va='top', wrap=True)
        ax.text(0.55, 0.95, right_text, fontsize=10, ha='left', va='top', wrap=True)

        pdf.savefig()
        plt.close()

    print(f"PDF report generated at: {pdf_path}")
```

Finally, the following file must be created in the root of the project:

### `main_simulator.py`

This file contains the instructions necessary to run the simulation and subsequently report the results:

```python
from simulator.simulator import main
from simulator.report_generator import generate_status_report_pdf

if __name__ == "__main__":
    main()
    generate_status_report_pdf("simulator/status_log.json")
```
### Run the simulation
To run the simulations you must execute the following command, making sure you have followed all the previous steps, with the system running:

```bash
    python .\main_simulator.py
```

After running this command, the system will automatically generate a PDF report with a summary of the results obtained. This .pdf file will be located in the previously created /simulator folder and will store the results in the simulator/status_log.json file.

