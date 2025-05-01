import requests
import threading

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoidGVzdF91c2VyIn0.NiAjMp8K9re-WJE_BJbqCmLBF4yFr0rDZwNRHj9Cbb8"

def make_request():
    try:
        headers = {"Authorization": f"{TOKEN}"}
        print("Enviando headers:", headers)  
        r = requests.get("http://127.0.0.1:8000/data", headers=headers)
        print(r.json())
    except Exception as e:
        print(f"Error: {e}")

threads = []
for _ in range(50):  # solo 1 para depurar
    t = threading.Thread(target=make_request)
    t.start()
    threads.append(t)

for t in threads:
    t.join()