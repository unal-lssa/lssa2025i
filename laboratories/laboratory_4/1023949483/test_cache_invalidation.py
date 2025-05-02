import requests
import time

URL = "http://localhost:8000/data"
CACHE_URL = "http://localhost:5004/cache/my_data"  # Directly hits cache

def print_divider(title):
    print("\n" + "=" * 30)
    print(title)
    print("=" * 30)

# Step 1: Fetch data to populate cache
print_divider("Step 1: First request (should hit DB)")
resp = requests.get(URL)
print(f"Response: {resp.json()}")

# Step 2: Fetch again (should hit cache)
print_divider("Step 2: Second request (should hit cache)")
resp = requests.get(URL)
print(f"Response: {resp.json()}")

# Step 3: Invalidate cache
print_divider("Step 3: Invalidate cache manually")
del_resp = requests.delete(CACHE_URL)
print(f"Delete cache response: {del_resp.json()}")

# Step 4: Fetch again (should hit DB)
print_divider("Step 4: After invalidation (should hit DB again)")
resp = requests.get(URL)
print(f"Response: {resp.json()}")
