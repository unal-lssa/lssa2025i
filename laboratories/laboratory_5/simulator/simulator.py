import requests
from Components.status_tracker import reset_log
data = {
    "username": "user1",
    "password": "password123"
}

main_loadbalancer = "http://127.0.0.1:8000"

def request_login():
    url = f"{main_loadbalancer}/login"
    headers = {"Content-Type": "application/json"}
    data = {
        "username": "user1",
        "password": "password123"
    }

    response = requests.post(url, json=data, headers=headers)
    data = response.json()
    returned_token = data.get("token")
    return returned_token

def request_data(token):
    url = f"{main_loadbalancer}/data"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def request_long_task(token):
    url = f"{main_loadbalancer}/longtask"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    body = {
        "task": "report"
    }
    response = requests.post(url, headers=headers, json=body)

    return response.json()



def run_simulation(token, purchase_count=300):


    print('-----------------Start requesting data-----------------')
    for i in range(1, purchase_count + 1):
        request_data(token)
    print('-----------------Start requesting longtask-----------------')
    for i in range(1, purchase_count + 1):
        request_long_task(token)

def main():
    reset_log()
    token = request_login()
    run_simulation(token)

