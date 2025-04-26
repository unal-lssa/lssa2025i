Owner: Lucas Peña Salas
ID: 1019147265

Instructions:

run the following command to start the server:
```bash
docker-compose up --build

Login as an admin user with the following req and copy the JWT tocken from the response:
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```
To create a blogpost, run the following command:
```bash
curl -X POST http://localhost:8000/blogposts \
  -H "Authorization: Bearer <REGULAR_USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Blog", "description": "This is my blog content."}'

```
To create a setting, run the following command:
```bash
curl -X POST http://localhost:8000/appsettings \
  -H "Authorization: Bearer <ADMIN_USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "maintenance_mode", "value": "off"}'
```
Login as a regular user with the following req and copy the JWT tocken from the response:
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"test_user": "user", "password": "password123"}'
```
Try to create a setting with the following command:
```bash
curl -X POST http://localhost:8000/appsettings \
  -H "Authorization: Bearer <REGULAR_USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "some_setting", "value": "should_fail"}'
```
You should get a 403 error, as the regular user does not have permission to create settings.
