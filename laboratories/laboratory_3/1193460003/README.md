Yosman Alexis Arenas Jimenez

# Laboratory 3 - Security

The objective of this lab is to demonstrate how applying the **Limit Exposure** security tactic using the **API Gateway** architectural pattern significantly reduces the system's attack surface. This is a core principle of **Secure by Design** — building security into the architecture from the start.

## Improvements worked

- **IP Whitelisting** to restrict routes.
- **Rate Limiting** on auth endpoints to prevent brute-force attacks.
- **Security Headers** like Authorization to avoid web vulnerabilities.

## Run project

1. Install dependencies
   ```bash
   pip install requests
   pip install flask
   ```

#### Start services

Run the following commands to start services

- **API Gateway** service:
  ```bash
  python api_gateway.py
  ```
- **Microservice** service:
  ```bash
  python microservice.py
  ```
- **Database** service:
  ```bash
  python database.py
  ```

#### Generate JWT

Execute the following curl:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "user1", "password": "password123"}' http://localhost:5000/login
```

This will return a token that you can use to access restricted routes.
