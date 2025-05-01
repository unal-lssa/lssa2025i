from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 2)  # tiempo entre requests de cada usuario

    @task
    def access_data(self):
        # Simula llamada autenticada al endpoint /data
        token_resp = self.client.post("/login", json={
            "username": "user1",
            "password": "password123"
        })

        if token_resp.status_code == 200:
            token = token_resp.json()["token"]
            headers = {"Authorization": token}
            self.client.get("/data", headers=headers)

    @task
    def trigger_long_task(self):
        # Simula una petición a /longtask
        token_resp = self.client.post("/login", json={
            "username": "user1",
            "password": "password123"
        })

        if token_resp.status_code == 200:
            token = token_resp.json()["token"]
            headers = {"Authorization": token}
            self.client.post("/longtask", json={"task": "process_data"}, headers=headers)
