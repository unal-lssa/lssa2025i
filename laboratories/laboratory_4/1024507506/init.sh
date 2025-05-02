#/bin/sh

python cache.py
python database.py
python microservice.py
python worker.py
python api_gateway.py  # Also run a second instance on port 5003 to simulate load balancing
python load_balancer.py