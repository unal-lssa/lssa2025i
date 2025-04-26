# Large-Scale Software Architecture  
## Laboratory 3 - Security
#### Julián Ricardo Beltrán Lizarazo - jrbeltranl@unal.edu.co - 1023949483

## Additional services
There are two new services that use the role and user information in the JWT:
- **clients-ms:** Returns all the clients information for `admin` roles and only owned clients information for `user` role.
- **admin-ms:** Accesible only for `admin` role. Returns the users information.

## Security improvements
### Authorization
The new services have an authorization layer that controls what information can each user see based on their roles. For this, there are two mechanisms in place.

- There is a new `admin_required` decorator implemented in the API Gateway, that requires the user to have an admin role in order to access a route
    ```python
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user.get("role") != "admin":
                return jsonify({'message': 'Admin privileges required!'}), 403
            return f(*args, **kwargs)
        return decorated_function
    ```
- The services have it's own logic for verifying the user's role and filter the information to return based on it. For example, for the clients_ms only showing the clients owned by the user (or all client information for admins)
    ```python
    @app.route('/clients', methods=['GET'])
    def get_clients():
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "Missing token"}), 403

        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username = payload.get("username")
            role = payload.get("role", "user")

            if role == "admin":
                return jsonify(CLIENTS)
            else:
                user_clients = [c for c in CLIENTS if c["owner"] == username]
                return jsonify(user_clients)
        except Exception as e:
            return jsonify({"message": f"Invalid token: {str(e)}"}), 403
    ```
### JWT Expiration Time
The JWT logic was modified so it also checks the expiration time for the tokens in the requests. Tokens will expire 30 minutes after they're issued. This ensures they have a limited lifespan, reducing the risk of unauthorized access if a token is compromised
```python
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    user = USERS.get(username)

    if user and user['password'] == password:
        expiration = datetime.utcnow() + timedelta(minutes=30)
        token = jwt.encode(
            {
                'username': username,
                'role': user['role'],
                'exp': expiration
            },
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({'token': token})
    
    return jsonify({'message': 'Invalid credentials'}), 401
```

### Network segregation
The services are placed in a private network, the only public component is the API Gateway, this adds an extra layer to the exposure limitting. Additionally, by containerizing the application, another layer of security is added, as the system components run in their own environments, self-contained and their only interactions are with computing resources.
```YAML
version: "3.9"

networks:
  private_network:
    driver: bridge
  public_network:
    driver: bridge

services:
  client:
    build:
      context: ./client
      dockerfile: Dockerfile
    ports:
      - "5003:5003"
    environment:
      - FLASK_APP=clients_ms.py
    networks:
      - private_network

  api_gateway:
    build:
      context: ./api_gateway
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_APP=api_gateway.py
    depends_on:
      - client
      - admin
    networks:
      - public_network
      - private_network

  admin:
    build:
      context: ./admin
      dockerfile: Dockerfile
    ports:
      - "5004:5004"
    environment:
      - FLASK_APP=admin_ms.py
    networks:
      - private_network
```
## Executing and testing
The application can be executed by running the `docker-compose up --build` command in the root of the project.

Once all the containers are running, in a different terminal, outside the docker environment, in the root of the project. The `python py .\test_scripts.py`command can be used to test the project.

This python file has a set of tests that cover the main scenarios that proof the implemented security improvements.

*Note: If the host IP is rejected by the application, it can be added to the api_gateway.py file - line 10 (AUTHORIZED_IPS = ["127.0.0.1", "172.19.0.1"])*