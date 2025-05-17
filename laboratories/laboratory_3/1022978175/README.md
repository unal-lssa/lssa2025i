# Laboratory 3 

## Nasem: Sergio Amdres Cabezas

## How to Test

This implemntation includes a reate limit decorator that applies the Detect Service Denial tactic.


Start all three services in separate terminals
Get a token from the login endpoint:

curl -X POST -H "Content-Type: application/json" -d '{"username": "user1", "password": "password123"}' http://127.0.0.1:5000/login

Use the token to access protected endpoints:

curl -X GET -H "Authorization: Bearer <your_token>" http://127.0.0.1:5000/data

Test the rate limiting by making more than 5 requests within 60 seconds - you should get a 429 response
Try accessing the microservice directly (this should fail):
curl http://127.0.0.1:5001/microservice