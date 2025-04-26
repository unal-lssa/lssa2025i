**FULL NAME**: Ivan Andres Lemus Moreno

**Steps**

1. Run `docker compose -f docker-compose.yml up -d --build`
2. Make the following request to obtain the JWT token

```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "user1", "password": "password123"}' http://127.0.0.1:5000/login
```

3. Copy the token obtained from the previous step
4. Run the following command, keep in mind that you must replace the `REPLACE_ME` placeholder by the token copied in the last step
```
curl --location 'http://127.0.0.1:5000/magic' \
--header 'Authorization: REPLACE_ME'
```
5. Run the request more than 6 times in less than a minute and you will be rate limited