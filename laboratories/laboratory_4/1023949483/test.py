import requests
import threading

GET_URL = "http://localhost:8000/data"
POST_URL = "http://localhost:8000/longtask"

def make_get_request(i):
    try:
        r = requests.get(GET_URL)
        print(f"[GET {i}] Status: {r.status_code} | Cached: {r.json().get('cached')}")
    except Exception as e:
        print(f"[GET {i}] Failed: {e}")

def make_post_request(i):
    try:
        payload = {"task": f"report_{i}"}
        r = requests.post(POST_URL, json=payload)
        print(f"[POST {i}] Status: {r.status_code} | Response: {r.json()}")
    except Exception as e:
        print(f"[POST {i}] Failed: {e}")

threads = []

# Simulate 20 parallel GET requests
print("Starting GET requests...")
for i in range(20):
    t = threading.Thread(target=make_get_request, args=(i,))
    threads.append(t)
    t.start()

# Wait for all GET threads to complete
for t in threads:
    t.join()

print("All GET requests completed.\n")

# Clear the threads list for POST requests
threads = []

# Simulate 20 parallel POST requests
print("Starting POST requests...")
for i in range(20):
    t = threading.Thread(target=make_post_request, args=(i,))
    threads.append(t)
    t.start()

# Wait for all POST threads to complete
for t in threads:
    t.join()

print("All POST requests completed.")