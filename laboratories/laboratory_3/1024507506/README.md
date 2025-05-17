# Laboratory 3 - Security (Limit Exposure with API Gateway & Centralized Authentication)

### ✅ Author

- **Name:** Jilkson Alejandro Pulido Cruz
- **ID:** 1024507506

## 🛡️ Objective
Demonstrate Secure by Design principles using the Limit Exposure tactic with an API Gateway and centralized authentication.

## 🚀 Improvements Implemented
- Added a hidden **Authentication Service** for centralized JWT management.
- API Gateway now delegates authentication, following best practices.
- **Role-Based Access Control (RBAC)** via JWT.
- **Rate Limiting** on login endpoint to prevent brute-force attacks.
- **IP Whitelisting** to restrict sensitive routes.
- Applied **Security Headers** to mitigate common web vulnerabilities.

## ⚙️ How to Run

1. Install dependencies:
   ```bash
pip install requests
pip install flask 



#### Start all services
Run the following commands to start each service in separate terminals:
1. **API Gateway**:
   ```bash
   python api_gateway.py
   ```
   The API Gateway will run on port `5000`.
   
2. **Microservice**:
   ```bash
   python microservice.py
   ```
   The microservice will run on port `5001`.
   
3. **Database**:
   ```bash
   python database.py
   ```
   The database will run on port `5002`.

4. **Authentication**
    ```bash
    python authentication_service.py
    ```
    The auth service run on port `5003`.
#### Obtain JWT Token

Use the `POST /login` endpoint to log in and get a JWT token.
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "user1", "password": "password123"}' http://127.0.0.1:5000/login
```
This will return a token that will be used to access protected routes.

#### Access Protected Routes

Use the `GET /data` endpoint in the API Gateway with the JWT token in the `Authorization` header.
```bash
curl -X GET -H "Authorization: Bearer <your_token>" http://127.0.0.1:5000/data
```


#### 🚫 Test Rate Limiting on /login

After 5 login attempts per minute from the same IP:

```bash

for i in {1..6}; do 
  curl -X POST -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "wrongpass"}' \
  http://127.0.0.1:5000/login
done
```


