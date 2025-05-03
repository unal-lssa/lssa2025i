# Lab 4 - Scalability

Name: Carlos Santiago Sandoval Casallas

## Proposed Architecture

- **Architecture:** client -> load_balancer_api_gateway -> api_gateway instances -> (load_balancer_service -> service instances -> database + cache) and (load_balancer_worker -> worker instances -> worker_cache);

- Authentication via load_balancer_auth -> auth_service instances;

## Ports

| Servicio                     | Puerto |
|------------------------------|--------|
| load_balancer_api_gateway    | 8000   |
| api_gateway_1                | 5000   |
| api_gateway_2                | 5001   |
| load_balancer_service        | 5002   |
| service_1                    | 5003   |
| service_2                    | 5004   |
| database                     | 5005   |
| cache                        | 5006   |
| load_balancer_worker         | 5007   |
| worker_1                     | 5008   |
| worker_2                     | 5009   |
| worker_cache                 | 5010   |
| auth_service_1               | 5011   |
| auth_service_2               | 5012   |
| load_balancer_auth           | 5013   |

## How to run

```bash
python3 load_balancer_api_gateway.py
python3 api_gateway_1.py 5000
python3 api_gateway_2.py 5001
python3 load_balancer_auth.py
python3 auth_service_1.py 5011
python3 auth_service_2.py 5012
python3 load_balancer_service.py
python3 service_1.py 5003
python3 service_2.py 5004
python3 database.py
python3 cache.py
python3 load_balancer_worker.py
python3 worker_1.py 5008
python3 worker_2.py 5009
python3 worker_cache.py
```

# How to test

```bash
# Get token
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Get data using token
curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/data

# Add task using token
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"task":"report"}' http://127.0.0.1:8000/longtask
```

### Note
- The logic of the load balancers has been modified to act as proxies. This is because the Flask redirection was causing me problems.