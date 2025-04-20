# Laboratory 3 - Security

Large Scale Software Architecture

Universidad Nacional de Colombia – 2025-I

---

## Student Information

Name: Santiago Suárez Suárez

Document ID: 1001326848

---

## Objective
The objective of this laboratory is to demonstrate how applying the **Limit Exposure** security tactic using the **API Gateway** architectural pattern significantly reduces the system's attack surface. This approach follows the **Secure by Design** principle, integrating security into the architecture from the start.

---

## Architecture Diagram

```mermaid
graph
	CL[Client]
    GW[API Gateway]

    subgraph Microservices
		TS[Tasks Service]
		PS[Projects Service]
	end

    TDB[(Tasks DB)]
    PDB[(Projects DB)]
	CL --> GW
    GW --> TS
    GW --> PS
    TS --> TDB
    PS --> PDB
```

---

## Architecture Decisions (Secure by Design)

### Security Tactic: Limit Exposure
- **What is Limit Exposure?**
  The **Limit Exposure** tactic focuses on reducing the visibility and accessibility of sensitive components. This is achieved by controlling who can interact with the system and which parts of the system are exposed.

- **Advantages of Limit Exposure:**
  - **Reduced Attack Surface:** Minimizes the number of entry points attackers can exploit.
  - **Granular Access Control:** Ensures only authorized services or users can interact with sensitive components.
  - **Regulatory Compliance:** Helps meet regulations like GDPR or HIPAA by restricting access to critical components.

### Implementation of Limit Exposure

To apply the **Limit Exposure** tactic, the following security measures were implemented:

1. **Using JWT in the API Gateway**:
   - The API Gateway validates JWT tokens for every request. If the token is invalid or missing, the request is rejected.
   - Example code in the API Gateway:

     ```python
        # Function to check JWT token
        def token_required(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                token = request.headers.get('Authorization')
                if not token:
                    return jsonify({'message': 'Token is missing!'}), 403
                try:
                    jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                except:
                    return jsonify({'message': 'Token is invalid!'}), 403
                return f(*args, **kwargs)
            return decorated_function

        # Route for user login (returns JWT token)
        @app.route('/login', methods=['POST'])
        def login():
            auth = request.get_json()
            username = auth.get('username')
            password = auth.get('password')
            if USERS.get(username) == password:
                token = jwt.encode({'username': username}, SECRET_KEY, algorithm="HS256")
                return jsonify({'token': token})
            return jsonify({'message': 'Invalid credentials'}), 401

        # Protected route
        @app.route('/data', methods=['GET'])
        @token_required
        def get_data():
            return jsonify({'message': 'Data accessed successfully!'}), 200.
     ```

2. **IP Restriction in Microservices**:
   - Microservices verify that requests originate only from the API Gateway.
   - Example code in a microservice:

     ```python
        ALLOWED_SERVICES = ["ms-task"]  # Servicios internos de Docker

        # Function to check if the request comes from an authorized IP address
        def limit_exposure(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = request.remote_addr
                client_host = request.host.split(':')[0]  # Extraer el nombre del host
                print(f"Request received from IP: {client_ip}, Host: {client_host}")

                if client_host not in ALLOWED_SERVICES:
                    print(f"Unauthorized access attempt from Host: {client_host}, IP: {client_ip}")
                    return jsonify({'message': 'Forbidden: Unauthorized Host', 'host': client_host, 'ip': client_ip}), 403
                return f(*args, **kwargs)
            return decorated_function

        @app.route('/task', methods=['GET'])
        @limit_exposure # Apply the limit exposure tactic to this route
        def get_tasks():
            # continue code ...
     ```

3. **Network Protection in Docker Compose**:
   - Private networks were configured in the `docker-compose.yml` file to isolate the containers.
   - Example configuration in `docker-compose.yml`:

     ```yaml
     version: '3.8'

     services:
       api_gateway:
         build: ./api_gateway
         ports:
           - "5000:5000"
         networks:
           - internal_network

       ms_task:
         build: ./ms_task
         networks:
           - internal_network

       ms_project:
         build: ./ms_project
         networks:
           - internal_network

       tasks_db:
         image: postgres
         networks:
           - internal_network

       projects_db:
         image: postgres
         networks:
           - internal_network

     networks:
       internal_network:
         driver: bridge
     ```

These implementations ensure that the system is secure and adheres to the **Limit Exposure** tactic, protecting internal components and significantly reducing the attack surface.

---

## Prerequisites

Ensure you have the following installed:

- Docker
- Python 3.x

---

## Setup - Using Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/unal-lssa/lssa2025i.git
   cd lssa2025i/laboratories/laboratory_3/1001326848
   ```

2. Build and start the services using Docker Compose:
   ```bash
   docker-compose up --build -d
   ```

3. The following services will be started:
   - **API Gateway**: Exposed on port `5000`.
   - **Microservice (ms-task)**: Accessible internally on port `5001`.
   - **Microservice (ms-project)**: Accessible internally on port `5002`.
   - **Databases**: `tasks_db` and `projects_db` for the microservices.

---

## API Endpoints

### API Gateway
- **POST /login**
  - **Description**: Authenticate a user and return a JWT token.
  - **Request Body**:
    ```json
    {
      "username": "user1",
      "password": "password123"
    }
    ```
  - **Response**:
    ```json
    {
      "token": "<jwt_token>"
    }
    ```

- **GET /data**
  - **Description**: Access protected data.
  - **Headers**:
    - `Authorization: Bearer <jwt_token>`
  - **Response**:
    ```json
    {
      "message": "Data accessed successfully!"
    }
    ```

- **GET /task**
  - **Description**: Access tasks from the `ms-task` microservice.
  - **Headers**:
    - `Authorization: Bearer <jwt_token>`
  - **Response**:
    ```json
    {
      "tasks": [...]
    }
    ```

- **GET /project**
  - **Description**: Access projects from the `ms-project` microservice.
  - **Headers**:
    - `Authorization: Bearer <jwt_token>`
  - **Response**:
    ```json
    {
      "projects": [...]
    }
    ```

---

## Testing the System

1. **Obtain a JWT Token**
   Use the `/login` endpoint to authenticate and retrieve a token:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"username": "user1", "password": "password123"}' http://localhost:5000/login
   ```

2. **Access Protected Endpoints**
   Use the token to access protected routes:
   - **Access `/data`:**
     ```bash
     curl -X GET -H "Authorization: <your_token>" http://localhost:5000/data
     ```
     - Example:

        ```bash
        curl -X GET -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIxIn0.2nSrDXt0I7TlXvocn_Z9qxGFnSHOvOyT3sboBgbkoCo" http://localhost:5000/task
        ```

        Response

        ```json
        {"tasks":[[1,"task 1"],[2,"task 2"],[3,"task 3"]]}
        ```

   - **Access `/task`:**
     ```bash
     curl -X GET -H "Authorization: <your_token>" http://localhost:5000/task
     ```

   - **Access `/project`:**
     ```bash
     curl -X GET -H "Authorization: <your_token>" http://localhost:5000/project
     ```

3. **Test Unauthorized Access**
   - Try accessing the API Gateway or microservices (ports 5001 and 5002) without a valid token or from an unauthorized IP. You should receive a `403 Forbidden` error.

        - Example:

            ```bash
            curl -X GET http://localhost:5001/task
            ```

            Response:

            ```json
            {"host":"localhost","ip":"172.19.0.1","message":"Forbidden: Unauthorized Host"}
            ```
---

## Conclusion

By applying the **Limit Exposure** tactic:
- We **reduced the attack surface** by exposing only the API Gateway.
- We **implemented JWT-based access control** to ensure only authorized users can interact with the system.
- We **restricted access by IP** to further limit which clients can access the system.

This proactive approach to security, integrated from the design phase, prevents vulnerabilities and reduces the risk of attacks.
