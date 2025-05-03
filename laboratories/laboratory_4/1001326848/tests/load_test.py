from locust import HttpUser, task, between, events
import uuid
import random

JWT_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIxIn0.xMpiGanjLuT9-P3BXbsI6pKa8BB2suAXkxltSwrGFOc"

# Register custom CLI argument
@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--mode", type=str, default="hit", help="Mode: 'hit' or 'miss'")

class CachingUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.headers = {
            "Authorization": JWT_TOKEN
        }
        self.mode = self.environment.parsed_options.mode

    @task
    def get_data_or_process(self):
        endpoint = random.choice(["/data", "/process"])

        if self.mode == "miss":
            key = str(uuid.uuid4())[:8]
            self.client.get(f"{endpoint}?key={key}", headers=self.headers)
        else:
            self.client.get(endpoint, headers=self.headers)
