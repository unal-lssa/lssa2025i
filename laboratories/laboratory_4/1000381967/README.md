# Laboratory 4
### Name: Juan Esteban Hunter Malaver
## Instructions to deploy:
1. Download the team2 branch :

    ```
    git pull origin team2
    ```
2. Navigate to the following directory:
    ```
    cd laboratories/laboratory_4/1000381967/
    ```
3. At this level, run the following command to build and start the containers:
    ```
    sudo docker compose up --build
    ```
4. Open two additional terminal windows:

    - The second terminal will be used to run the curl requests.

    - The third terminal will be attached to the worker container to monitor the worker logs while it consumes the task queue:
        ```
        sudo docker attach 1000381967-worker-1
        ```

5. In the second terminal, authenticate using this command to obtain a token:
    ```
    curl -s http://localhost:8000/auth   -H "Content-Type: application/json"   -d '{"username":"user1", "password":"password1"}'
    ```
    This request will return a token similar to the following, which should be used in subsequent requests:

    ```
    {"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIxIiw..."}
    ```

    Note: This token is only valid for one hour.

6. Use the token to query the products microservice via the API Gateway (through the load balancer):

    ```
    curl http://localhost:8000/data -H "Content-Type: application/json" -H "Authorization: <Your token>"
    ```

    The response will look like this the first time (not cached):

    ```
    {"cached":false,"products":[{"id":1,"name":"Frutino","price":2000.0},{"id":2,"name":"Quipitos","price":1500.0},{"id":3,"name":"Vive100","price":3000.0},{"id":4,"name":"Nutribela","price":25000.0}]}
    ```
    If you make the request again within 60 seconds, the response will be cached (Via Redis):

    ```
    {"cached":true,"products":[{"id":1,"name":"Frutino","price":2000.0},{"id":2,"name":"Quipitos","price":1500.0},{"id":3,"name":"Vive100","price":3000.0},{"id":4,"name":"Nutribela","price":25000.0}]}
    ```
7. To test RabbitMQ queue processing, run the following loop in the second terminal:
    ```
    for i in {1..5}; do   curl -X POST http://localhost:8000/longtask        -H "Content-Type: application/json"        -H "Authorization: <Your Token>"  -d '{"task": "reporte número '$i'"}'; done
    ```

    This will produce the following responses in the second terminal:

    ```
    {"status":"Task queued"}
    {"status":"Task queued"}
    {"status":"Task queued"}
    {"status":"Task queued"}
    {"status":"Task queued"}
    ```

    And in the third terminal (worker logs), you should see:

    ```
    Procesando tarea: {'task': 'reporte número 1'}
    Tarea completada
    Procesando tarea: {'task': 'reporte número 2'}
    Tarea completada
    Procesando tarea: {'task': 'reporte número 3'}
    Tarea completada
    Procesando tarea: {'task': 'reporte número 4'}
    Tarea completada
    Procesando tarea: {'task': 'reporte número 5'}
    Tarea completada
    ```

