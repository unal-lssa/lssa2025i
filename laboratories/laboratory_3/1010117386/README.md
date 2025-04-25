# Daniel Santiago Mendoza Morales

# Run the lab

Have docker and docker compose.

docker compose up -d

# Stop the lab and remove images

docker compose down --rmi all

# Explanation

Using docker compose we can limit the exposure of microservice and database services by not exposing their ips. The only service exposed is api gateway. Also we can limit responses received by the microservice and db. When microservice receives wrong response from db it will return a generic error instead of returning db actual error. Same happens when api connects to microservice. This allows us to further limit the exposure of microservice and db actual behaviors.
