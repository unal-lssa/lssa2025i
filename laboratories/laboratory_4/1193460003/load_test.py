import threading
import time
import requests

URL = "http://127.0.0.1:8000/data"
CLIENTS = 50
REQUESTS_PER_CLIENT = 20

latencies = []
def worker():
    for _ in range(REQUESTS_PER_CLIENT):
        start = time.time()
        try:
            r = requests.get(URL)
            latencies.append(time.time() - start)
        except:
            latencies.append(None)

threads = []
for i in range(CLIENTS):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()
for t in threads:
    t.join()

# Report simple métricas
success = sum(1 for l in latencies if l is not None)
failures = sum(1 for l in latencies if l is None)
avg = sum(l for l in latencies if l) / success
print(f"Success: {success}, Failures: {failures}, Avg Latency: {avg:.3f}s")