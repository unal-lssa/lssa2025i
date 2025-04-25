# Enhanced Secure Microservices Architecture

**Full Name:** Juan Andres Orozco Velandia

## Project Overview
This project demonstrates an enhanced implementation of the Limit Exposure security tactic using the API Gateway architectural pattern. It includes multiple microservices with advanced security features, all containerized using Docker.

## Architecture

```
Client → API Gateway → [Auth Service, User Service, Product Service, Logging Service] → Database
```

Each service is isolated in its own container with specific exposure rules:
- **API Gateway**: Public-facing with advanced security mechanisms
- **Auth Service**: Internal service for authentication and authorization 
- **User Service**: Protected microservice for user management
- **Product Service**: Protected microservice for product management
- **Logging Service**: Internal service for security event tracking

## Security Features

1. **Advanced Limit Exposure Implementation:**
   - Role-Based Access Control (RBAC)
   - Service-to-service authentication with API keys
   - IP whitelisting with subnet support
   - Rate limiting
   - Request validation and sanitization
   - Circuit breaker pattern
    - JWT with enhanced validation

## Running the Application

1. Clone the repository
2. Navigate to the project directory
3. Run the application using Docker Compose:

```bash
docker-compose up -d
```

4. The API Gateway will be accessible at http://localhost:5000

## Testing the Security Features

1. **Obtain authentication token:**

Login as admin:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}' http://localhost:5000/auth/login
```
Login as user:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "user1", "password": "password123"}' http://localhost:5000/auth/login
```

2. **Access Role based protected resources (with token):**

Access users list (both admin and normal user can access):
```bash
curl -X GET -H "Authorization: Bearer <your_token_here>" http://localhost:5000/users
```
Create a new user (admin only):
```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <your_token_here>" -d '{"username": "newuser", "email": "newuser@example.com", "role": "USER"}' http://localhost:5000/users
```
Create a new product (admin only):
```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <your_token_here>" -d '{"name": "New Product", "price": 199.99, "description": "A test product"}' http://localhost:5000/products
```
3. **Test rate limiting:**
Rate limiting is configured differently for admin users (100 requests/minute) and regular users (10 requests/minute).

Run this Python script to test rate limiting with different roles:

```python
import requests
import time
import sys

def test_rate_limit(token, endpoint, requests_count):
    headers = {"Authorization": f"Bearer {token}"}
    success = 0
    rate_limited = 0
    
    print(f"Sending {requests_count} rapid requests...")
    for i in range(requests_count):
        response = requests.get(f"http://localhost:5000/{endpoint}", headers=headers)
        if response.status_code == 200:
            success += 1
        elif response.status_code == 429:  # Rate limit exceeded
            rate_limited += 1
            print(f"Rate limit reached after {success} requests")
            break
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
    
    print(f"Results: {success} successful requests, {rate_limited} rate limited")
    return success, rate_limited

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python rate_limit_test.py <token> <role>")
        sys.exit(1)
    
    token = sys.argv[1]
    role = sys.argv[2].upper()
    
    # Test rate limits based on role
    if role == "ADMIN":
        print("Testing rate limits for ADMIN role (limit: 100 req/min)")
        test_rate_limit(token, "products", 105)
    else:
        print("Testing rate limits for USER role (limit: 10 req/min)")
        test_rate_limit(token, "products", 15)
```
Save this as rate_limit_test.py and run:
```bash
# For admin user
python rate_limit_test.py your_admin_token ADMIN

# For regular user
python rate_limit_test.py your_user_token USER
```

4. **Test Product Service:**

List all products:
```bash
curl -X GET -H "Authorization: Bearer <your_token_here>" http://localhost:5000/products
```

Get specific product (ID = 1):
```bash
curl -X GET -H "Authorization: Bearer <your_token_here>" http://localhost:5000/products/1
```

5. **Test Logging Service (Admin only):**

View all logs (through API Gateway):
```bash
curl -X GET -H "Authorization: Bearer <your_admin_token>" http://localhost:5000/logs
```

Filter logs by event type:
```bash
curl -X GET -H "Authorization: Bearer <your_admin_token>" "http://localhost:5000/logs?event_type=UNAUTHORIZED_ROLE_ACCESS"
```