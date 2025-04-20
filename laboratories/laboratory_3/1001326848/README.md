# Laboratory 3 - Security
---

Large Scale Software Architecture

Universidad Nacional de Colombia – 2025-I

## Student Information
---

Name: Santiago Suárez Suárez

Document ID: 1001326848

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
