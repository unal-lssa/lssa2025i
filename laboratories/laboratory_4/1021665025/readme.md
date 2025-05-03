# [LSSA_2025i] - Laboratory 4 - Scalability

---

Name: Santiago Restrepo Rojas 

Citizenship ID: 1021665025 

Course: Large-Scale Software Architecture

Date: May 2, 2025

---

## Laboratory Objective and Context

This laboratory is based on the objectives outlined in the "[LSSA_2025i] - U4 - Laboratory 4.pdf" document. The primary goal was to demonstrate how applying *Performance and Scalability* tactics using architectural patterns such as **Load Balancing** and **Caching** can enhance a system's responsiveness and capacity to handle increased load. The original lab proposed a simplified architecture with a Load Balancer distributing requests to scaled API Gateway instances, incorporating caching and asynchronous task processing to offload work from the main request path.

I have implemented the core principles of Laboratory 4 by integrating Load Balancing, Caching, and Asynchronous Processing capabilities into the microservice architecture I developed in Laboratory 3, based on the Casitas Empire case study.

## Building upon Laboratory 3: The Casitas Empire Security Architecture

In Laboratory 3, I developed the foundational microservice architecture for the **Casitas Empire** rental management system, prioritizing **Security by Design**. This system manages sensitive data related to rental units, finances, legal documents, users, and roles. The architecture I implemented included several key security tactics:

* **Limit Exposure (API Gateway):** An API Gateway served as the single entry point, protecting internal microservices (Auth, Finances, Legal, Units) and their dedicated databases from direct external access.
* **Denial of Service Detection (Rate Limiting):** I implemented basic rate limiting in the API Gateway to protect against simple DoS attacks.
* **Separate Entities (Data Partitioning):** I divided the system into independent microservices, each with its own database (`auth_db`, `finances_db`, `legal_db`, `units_db`), ensuring logical separation and data independence.
* **Authorized Actors (RBAC):** I implemented Role-Based Access Control via the Authentication Service and enforced it in the API Gateway using JWT and role checks, ensuring only authorized users could access specific resources.

This established a secure foundation for the Casitas Empire system before focusing on scalability.

## Expanding for Scalability: Applying Laboratory 4 Tactics to Casitas Empire

For Laboratory 4, I enhanced the existing Casitas Empire architecture by incorporating the scalability tactics and patterns introduced in the lab document. My goal was to make the system more performant and capable of handling a larger number of users and requests.

### Architectural Changes

The improved architecture I designed now includes:

* **Client**
* **Nginx Load Balancer**: The new primary entry point, distributing traffic to multiple API Gateway instances.
* **API Gateways (Multiple Instances)**: Handling request routing, authentication, authorization, and **Caching** interactions.
* **Microservices (Finances, Legal, Units, Auth)**: Remaining responsible for core business logic and data management.
* **Redis**: A dedicated service used as a distributed **Cache**.
* **RabbitMQ**: A dedicated **Message Queue** for asynchronous task communication.
* **Celery Worker**: A separate service that consumes tasks from RabbitMQ and performs **Asynchronous Processing**.
* **Dedicated Databases (PostgreSQL)**: Remaining the persistent data stores for each microservice.

### Detailed Implementation of Scalability Tactics

I implemented the following scalability tactics:

1.  **Introduce Concurrency (Load Balancing):**
    * **Pattern:** **Load Balancing** using **Nginx**. I replaced the simple Flask load balancer with a robust Nginx server.
    * **Implementation:** I updated the `docker-compose.yml` to include an `nginx` service. I configured this service to act as a reverse proxy. It defines an `upstream` group containing the internal network addresses of the two `api_gateway` service instances (`api_gateway_1:5000` and `api_gateway_2:5000`). Nginx's default Round Robin algorithm distributes incoming requests across these gateway instances.
    * **Shifted Security:** I moved the **IP Restriction** (`allow`/`deny`) and **Rate Limiting** (`limit_req_zone`, `limit_req`) previously handled by the Flask API Gateway to the Nginx configuration, centralizing these access control measures at the entry point before requests even reach the application code. I updated the Flask API Gateway code to remove these decorators and logic.

2.  **Reduce Computational Overhead (Caching):**
    * **Pattern:** **Caching** using **Redis**. I integrated a dedicated, external cache store.
    * **Implementation:** I updated the `docker-compose.yml` to include a `redis` service using the official Redis image. I modified the Flask API Gateway (`api_gateway.py`), it now uses the `redis` Python client library to interact directly with the Redis service.
    * For endpoints like `/units/available`, the API Gateway now first attempts to fetch data from Redis using a key derived from the request. If data is found (Cache Hit), it is returned immediately. If not (Cache Miss), the API Gateway fetches data from the respective microservice, stores it in Redis with a Time-To-Live (TTL) for a specified duration, and then returns the data. This reduces the load on the microservices and databases for frequently accessed data.

3.  **Asynchronous Processing:**
    * **Technologies:** I introduced **RabbitMQ** as the message queue and **Celery** as the Python task queue framework. I chose **RabbitMQ** for its reliability, flexible routing, and priority support, and **Celery** for its robust integration with RabbitMQ and ease of use for Python distributed tasks.
    * **Implementation:**
        * I updated the `docker-compose.yml` to include `rabbitmq` and `celery_worker` services. RabbitMQ runs the message broker, and `celery_worker` runs the Celery worker process.
        * I updated the `api_gateway.py` to include Celery configuration pointing to the RabbitMQ broker and Redis (used as a backend to store task results/status). I added new routes (`/finances/generate_report`, `/legal/generate_report`) to the API Gateway.
        * When these new endpoints are hit (after passing security checks), the API Gateway does *not* generate the report directly. Instead, it calls the `.apply_async()` method on the respective Celery task objects (`generate_finances_report_task`, `generate_legal_report_task`).
        * This sends a message to RabbitMQ containing the task details. I configured two queues: `high_priority` for finance reports and `low_priority` for legal reports, assigning priority levels (0 for high, 5 for low) to the tasks sent to these queues.
        * I created a new `celery_worker` directory containing the `celery_app.py`. This file defines the Celery application (configured with the same RabbitMQ and Redis connections) and the actual implementation of the task functions (`generate_finances_report_task`, `generate_legal_report_task`). These functions include logic to connect to their respective databases (Finances and Legal) using SQLAlchemy and fetch the necessary data to simulate report generation. I included the necessary SQLAlchemy model definitions directly in `celery_worker/celery_app.py` for the worker to access the database schemas.
        * The `celery_worker` service's command in `docker-compose.yml` is configured to run the Celery worker process, specifying which queues to listen to (`high_priority`, `low_priority`). The worker continuously consumes messages from these queues, executing the tasks with higher priority tasks being processed before lower priority ones.

### Scalability Benefits

These new components significantly enhance the system's scalability:

* **Load Balancing:** By distributing incoming requests across multiple API Gateway instances, the Nginx Load Balancer prevents a single instance from becoming a bottleneck and allows the system to handle a higher volume of concurrent requests simply by adding more API Gateway replicas.
* **Caching:** The Redis cache reduces the number of requests that need to reach the microservices and databases, especially for read-heavy endpoints like fetching available units or transaction lists. This lowers the load on backend services, improves response times for cached data, and allows the microservices to handle more unique or write requests.
* **Asynchronous Processing:** By offloading long-running report generation tasks to the Celery worker, the main request path in the API Gateway remains free to handle incoming client requests quickly. This prevents the API Gateway from becoming unresponsive and allows the system to initiate many long tasks without blocking its core functionality. The use of RabbitMQ provides a buffer and ensures task reliability, while priorities ensure critical tasks (like finance reports) are processed sooner.

### Execution Steps

1.  **Build Docker Images:** Build the Docker images for all services.
    ```bash
    docker-compose build
    ```
2.  **Initialize Databases and Message Queue (if needed):** If this is your first time running or if you made changes to `schema.sql` files or want a clean state, remove existing volumes before starting.
    ```bash
    docker-compose down -v
    ```
3.  **Start Services:** Start all the containers defined in `docker-compose.yml`. This will bring up the databases, RabbitMQ, Redis, API Gateway instances, Nginx, and the Celery worker.
    ```bash
    docker-compose up -d # Use -d for detached mode
    ```
4.  **Obtain JWT Token:** Make a POST request to the Nginx Load Balancer's login endpoint (`http://localhost/login` or `http://127.0.0.1/login`) with the username and password of a test user (e.g., `test_admin` / `password123`). Remember Nginx is now on port 80.
    ```bash
    curl -X POST [http://127.0.0.1/login](http://127.0.0.1/login) \
    -H "Content-Type: application/json" \
    -d '{"username": "test_admin", "password": "password123"}'
    ```
    This will return a JWT token.
5.  **Access Cached Endpoints:** Use the obtained JWT token to access protected cached endpoints via Nginx (`/units/available`). Observe the logs in the API Gateway and Redis containers to see cache hits and misses.
    Access the public cached endpoint (`/units/available`) via Nginx (no token needed).
    ```bash
    curl -X GET [http://127.0.0.1/units/available](http://127.0.0.1/units/available)
    ```
6. **Trigger Async Tasks:** Make POST requests to the report generation endpoints via Nginx (`/finances/generate_report`, `/legal/generate_report`) with the appropriate token and roles.
    ```bash
    curl -X POST [http://127.0.0.1/finances/generate_report](http://127.0.0.1/finances/generate_report) \
    -H "Authorization: Bearer <your_token>" \
    -H "Content-Type: application/json" \
    -d '{}' # Empty body or add report parameters
    ```
11. **Test Security Features:** Verify IP restriction and Rate Limiting are enforced by Nginx (accessing from unauthorized IPs or sending too many requests to port 80). Verify authentication (accessing protected endpoints without a token) and RBAC (accessing protected endpoints with insufficient roles) are enforced by the API Gateway.
12. **Stop Services:** When finished, stop the running containers.
    ```bash
    docker-compose down
    ```

### Conclusion

This laboratory successfully demonstrated the application of Performance and Scalability tactics to the Casitas Empire security architecture that I built in the previous lab. By integrating an Nginx Load Balancer, a Redis Cache, and a robust Asynchronous Processing system using RabbitMQ and Celery, I transformed the initial secure microservices into a more performant, responsive, and scalable system capable of handling increased traffic and offloading time-consuming operations. This reinforces the importance of considering both security and scalability early in the large-scale software architecture design process.