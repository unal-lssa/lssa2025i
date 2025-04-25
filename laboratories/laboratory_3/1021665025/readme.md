# [LSSA_2025i] - Laboratory 3 - Security

---

Name: Santiago Restrepo 

Citizenship ID: 1021665025 

Course: Large-Scale Software Architecture

Date: April 25, 2025

---

## Laboratory Objective and Context

The primary goal was to demonstrate the application of the **Limit Exposure** security tactic using the **API Gateway** architectural pattern to reduce a system's attack surface. The original lab proposed a simple architecture consisting of a Client, API Gateway, Microservice, and Database, showing how hiding components behind the gateway enhances security. It emphasized the principle of **Secure by Design**, integrating security from the initial architectural phase. The lab also introduced basic IP restriction and JWT-based access control as means to limit exposure.

I have implemented the core concepts of the original lab, including the API Gateway and the idea of protecting backend services. However, as an extension and improvement upon the base exercise, I applied the principles to a new case study and incorporated additional security tactics and patterns as required by the lab's deliverable.

## Case Study: Casitas Empire

The case study for this extended laboratory is "Casitas Empire," a custom information system designed for a rental company located in Texas, USA. This system manages critical data including rental units, landlords, tenants, geographical locations, financial transactions, payment gateways, and legal documents such as lease agreements.

Given the sensitive nature of the data handled by Casitas Empire (personal information, financial records, legal contracts), applying robust security principles by design is paramount for its correct and secure operation. The system requires several key security considerations:

1.  **Limit Exposure:** A clear separation between public and private information is needed. An API Gateway should control access, allowing public view of available units while requiring authorization for sensitive tenant, financial, or legal data.
2.  **Denial of Service Detection:** The system must be resilient to overload or malicious attempts to disrupt service. Implementing a mechanism to control request rates is necessary to prevent DoS attacks.
3.  **Separate Entities:** Due to the diverse nature of the data (financial, legal, unit information), a logical separation is required. Data should be partitioned based on content and managed independently to ensure scalability, fault tolerance, and separation of concerns.
4.  **Authorized Actors:** Strict access control based on user roles is essential. Only authorized personnel (e.g., finance team, legal team) should be able to access and modify specific types of sensitive information, ensuring data integrity and compliance.

## Detailed Implementation

To address the security requirements of the Casitas Empire case study and expand upon the original laboratory's objective, I designed and implemented a microservice-based architecture orchestrated using Docker Compose.

### Architectural Design

The system architecture is composed of:

* An **API Gateway**: Serving as the single entry point for all client requests.
* An **Authentication Service**: Handling user registration, authentication, and providing user role information.
* Independent **Microservices**: `Finances Service`, `Legal Service`, and `Units Service`, each responsible for managing its specific domain data.
* Dedicated **Databases**: Each microservice has its own PostgreSQL database (`auth_db`, `finances_db`, `legal_db`, `units_db`) to ensure data partitioning and independence.

Docker Compose is used to define, build, and run this multi-container application, managing the network, service dependencies, and database initialization.

### Applied Security Tactics and Patterns

I implemented the following security tactics using specific architectural patterns:

1.  **Limit Exposure:**
    * **Pattern:** **API Gateway**. The `api_gateway` service is the only component directly exposed to external clients via port 5000. All microservices and databases are hidden within the internal Docker network, only accessible through the gateway.
    * **Implementation:** The `api_gateway.py` routes incoming requests to the appropriate internal microservice endpoint based on the URL path.
    * **IP Restriction:** The `@limit_exposure` decorator from the original lab was kept to demonstrate IP-based access control on certain routes.

2.  **Denial of Service Detection:**
    * **Pattern:** **Rate Limiting**. I implemented a basic rate-limiting mechanism to control the number of requests from a single IP address over a given time window.
    * **Implementation:** The `@rate_limited` decorator in `api_gateway.py` tracks incoming request timestamps per IP. If the rate exceeds a defined threshold (e.g., 500 requests per minute), subsequent requests from that IP are rejected with a `429 Too Many Requests` status. This is applied to all routes in the API Gateway.

3.  **Separate Entities:**
    * **Pattern:** **Data Partitioning**. The overall system data is partitioned based on domain logic (Authentication, Finances, Legal, Units).
    * **Implementation:** Each microservice (`auth_service`, `finances_service`, `legal_service`, `units_service`) has its own independent PostgreSQL database instance (`auth_db`, `finances_db`, `legal_db`, `units_db`). This separation is enforced at the data layer.
    * Each microservice manages its data using SQLAlchemy ORM and has its own dedicated database schema defined in a `schema.sql` file, applied automatically by Docker during database container initialization.

4.  **Authorized Actors:**
    * **Pattern:** **Role-Based Access Control (RBAC)**. Access to specific functionalities and data within the microservices is restricted based on the user's assigned role(s).
    * **Implementation:**
        * The `auth_service` manages users and roles (`user`, `admin`, `super_admin`, `finance`, `legal`, `finance_assistance`, `legal_assitance`) and their assignments in its database. It provides an endpoint (`/auth/user/<user_id>/roles`) to retrieve a user's roles.
        * Upon successful login via the API Gateway (which forwards the request to the `auth_service`), a JWT token is issued containing basic user information.
        * The `@token_required` decorator in the `api_gateway.py` validates the JWT. For a valid token, it makes an internal call to the `auth_service` to fetch the user's current roles and stores them in Flask's `g` object for the duration of the request.
        * The `@requires_role` decorator in the `api_gateway.py` is applied to protected routes. It checks if the user's roles (fetched by `@token_required`) intersect with the list of roles required for that specific route. If no matching role is found, a `403 Forbidden` error is returned.
        * Different routes in the API Gateway proxy to the microservices with varying role requirements (e.g., access to `/finances/transactions` requires `finance` or `finance_assistance` roles, while `/units/available` is public).

### Project Components and Implementation Details

The project is structured into directories for each service: `api_gateway`, `auth_service`, `finances_service`, `legal_service`, and `units_service`, along with a root `docker-compose.yml` and `README.md`.

* **`docker-compose.yml`**: Defines all services (`api_gateway`, microservices, databases), their build contexts, ports, environment variables (including database connection strings and the JWT secret key), dependencies, and volumes for data persistence and schema initialization.
* **`api_gateway/`**:
    * `Dockerfile`: Builds the Python environment with necessary libraries (`Flask`, `PyJWT`, `requests`).
    * `requirements.txt`: Lists Python dependencies.
    * `api_gateway.py`: Contains the Flask application for the gateway, including the `@limit_exposure`, `@rate_limited`, `@token_required`, and `@requires_role` decorators, the `/login` endpoint forwarding to the auth service, and proxy routes for `/data` (example protected route), `/finances/transactions`, `/legal/documents`, and `/units/available` with appropriate security decorators applied.
* **`auth_service/`**:
    * `Dockerfile`: Builds the Python environment (`Flask`, `SQLAlchemy`, `psycopg2-binary`, `PyJWT`, `bcrypt`).
    * `requirements.txt`: Lists Python dependencies.
    * `schema.sql`: Defines the `users`, `roles`, and `user_roles` tables and inserts the predefined roles and sample test users with hashed passwords (`password123`).
    * `models.py`: Defines SQLAlchemy ORM models for `User` and `Role`.
    * `app.py`: Contains the Flask application for authentication, including endpoints for user registration (`/auth/register`), login (`/auth/login`), and fetching user roles (`/auth/user/<user_id>/roles`). It uses bcrypt for password hashing.
* **`finances_service/`**:
    * `Dockerfile`: Builds the Python environment (`Flask`, `SQLAlchemy`, `psycopg2-binary`).
    * `requirements.txt`: Lists Python dependencies.
    * `schema.sql`: Defines the `transactions` table and inserts sample financial transaction records.
    * `models.py`: Defines the SQLAlchemy ORM model for `Transaction`.
    * `app.py`: Contains the Flask application for the finances service with an endpoint to fetch transactions (`/finances/transactions`).
* **`legal_service/`**:
    * `Dockerfile`: Builds the Python environment (`Flask`, `SQLAlchemy`, `psycopg2-binary`).
    * `requirements.txt`: Lists Python dependencies.
    * `schema.sql`: Defines the `legal_documents` table and inserts sample legal document records.
    * `models.py`: Defines the SQLAlchemy ORM model for `LegalDocument`.
    * `app.py`: Contains the Flask application for the legal service with an endpoint to fetch documents (`/legal/documents`).
* **`units_service/`**:
    * `Dockerfile`: Builds the Python environment (`Flask`, `SQLAlchemy`, `psycopg2-binary`).
    * `requirements.txt`: Lists Python dependencies.
    * `schema.sql`: Defines the `rental_units` table and inserts sample rental unit records.
    * `models.py`: Defines the SQLAlchemy ORM model for `RentalUnit`.
    * `app.py`: Contains the Flask application for the units service with an endpoint to fetch available units (`/units/available`).

### Execution Steps

1.  **Clone the Repository:** Clone the repository containing this project structure.
2.  **Navigate to Project Directory:** Open your terminal or command prompt and navigate to the root directory of the cloned project (where `docker-compose.yml` is located).
3.  **Generate Password Hashes:** If you modified the `schema.sql` files with different passwords or want to ensure the test users are correctly set up, run a Python script to generate bcrypt hashes for the desired test password (`password123` or similar) and update the `password_hash` values in `auth_service/schema.sql`.
4.  **Build Docker Images:** Build the Docker images for all services.
    ```bash
    docker-compose build
    ```
5.  **Initialize Databases (if needed):** If this is your first time running or if you made changes to the `schema.sql` files and need a clean database state, remove existing volumes before starting.
    ```bash
    docker-compose down -v
    ```
6.  **Start Services:** Start all the containers defined in `docker-compose.yml`. The databases will start first, initialized by the `schema.sql` files, followed by the microservices and the API Gateway.
    ```bash
    docker-compose up -d # Use -d for detached mode
    ```
7.  **Obtain JWT Token:** Make a POST request to the API Gateway's login endpoint (`http://localhost:5000/login` or `http://127.0.0.1:5000/login`) with the username and password of a test user (e.g., `test_admin` / `password123`).
    ```bash
    curl -X POST [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login) \
    -H "Content-Type: application/json" \
    -d '{"username": "test_admin", "password": "password123"}'
    ```
    This will return a JWT token.
8.  **Access Protected Endpoints:** Use the obtained JWT token to access protected endpoints via the API Gateway (e.g., `/data`, `/finances/transactions`, `/legal/documents`). Include the token in the `Authorization` header as `Bearer <your_token>`. Ensure the user role associated with the token has the necessary permissions for the endpoint you are trying to access, as defined by the `@requires_role` decorator in `api_gateway.py`.
    ```bash
    curl -X GET [http://127.0.0.1:5000/finances/transactions](http://127.0.0.1:5000/finances/transactions) \
    -H "Authorization: Bearer <your_token>"
    ```
    Test with different users and roles to verify RBAC.
9.  **Access Public Endpoints:** Access public endpoints (e.g., `/units/available`) which only require rate limiting.
    ```bash
    curl -X GET [http://127.0.0.1:5000/units/available](http://127.0.0.1:5000/units/available)
    ```
10. **Test Security Features:**
    * Try accessing protected endpoints without a token, with an invalid token, or with a token from a user lacking the required role (expect 401 or 403 errors).
    * If `@limit_exposure` is active and not configured for your IP, try accessing from an unauthorized IP (expect 403).
    * Send a large number of requests rapidly to any endpoint to trigger the rate limit (expect 429).
11. **Stop Services:** When finished, stop the running containers.
    ```bash
    docker-compose down
    ```