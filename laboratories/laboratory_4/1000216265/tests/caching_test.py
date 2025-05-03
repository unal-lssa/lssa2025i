import requests
import time
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os

def get_token():
    """Get an authentication token from the API Gateway"""
    try:
        response = requests.get("http://localhost:8000/token")
        return response.json().get('token')
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def test_caching(iterations=5, requests_per_iteration=10):
    """Test caching performance comparing cache hits vs. misses"""
    token = get_token()
    if not token:
        print("Failed to get authentication token")
        return
    
    print(f"Running caching test with {iterations} iterations and {requests_per_iteration} requests per iteration")
    headers = {"Authorization": token}
    
    # First, make sure cache is empty by flushing it
    try:
        requests.post("http://localhost:5004/cache/flush")
        print("Cache flushed")
    except Exception as e:
        print(f"Error flushing cache: {e}")
    
    # Run test over multiple iterations
    cache_hit_times = []
    cache_miss_times = []
    
    for iteration in range(iterations):
        # Generate a unique cache key for this iteration
        key = f"test_key_{iteration}"
        print(f"\nIteration {iteration+1}/{iterations} (key={key})")
        
        # First request (expected cache miss)
        print("Making first request (cache miss expected)...")
        start_time = time.time()
        response = requests.get(f"http://localhost:8000/data?key={key}", headers=headers)
        miss_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            is_cached = data.get('cached', False)
            if not is_cached:
                cache_miss_times.append(miss_time)
                print(f"Cache MISS confirmed: response time = {miss_time:.4f}s")
            else:
                print(f"Unexpected cache HIT on first request: {miss_time:.4f}s")
        else:
            print(f"Request failed with status code: {response.status_code}")
        
        # Subsequent requests (should be cache hits)
        print(f"Making {requests_per_iteration-1} subsequent requests (cache hits expected)...")
        hit_times = []
        for req in range(requests_per_iteration - 1):
            start_time = time.time()
            response = requests.get(f"http://localhost:8000/data?key={key}", headers=headers)
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                is_cached = data.get('cached', False)
                if is_cached:
                    hit_times.append(request_time)
                    print(f"  Request {req+1}: Cache HIT confirmed: {request_time:.4f}s")
                else:
                    print(f"  Request {req+1}: Unexpected cache MISS: {request_time:.4f}s")
            else:
                print(f"  Request {req+1}: Failed with status code: {response.status_code}")
        
        # Average hit time for this key
        if hit_times:
            avg_hit_time = sum(hit_times) / len(hit_times)
            cache_hit_times.append(avg_hit_time)
            print(f"Average cache hit time for this key: {avg_hit_time:.4f}s")
    
    # Print overall results
    print("\n===== RESULTS =====")
    
    avg_miss_time = sum(cache_miss_times) / len(cache_miss_times) if cache_miss_times else 0
    avg_hit_time = sum(cache_hit_times) / len(cache_hit_times) if cache_hit_times else 0
    
    print(f"Average cache miss time: {avg_miss_time:.4f}s")
    print(f"Average cache hit time: {avg_hit_time:.4f}s")
    
    if avg_hit_time > 0:
        speedup = avg_miss_time / avg_hit_time
        print(f"Speedup factor: {speedup:.2f}x")
    
    # Create comparison chart
    plt.figure(figsize=(10, 6))
    plt.bar(['Cache Miss', 'Cache Hit'], [avg_miss_time, avg_hit_time])
    plt.title('Average Response Time: Cache Hit vs Miss')
    plt.ylabel('Time (s)')
    plt.grid(axis='y', alpha=0.3)
    
    # Add speedup text
    if avg_hit_time > 0:
        plt.text(0.5, avg_miss_time/2, f"{speedup:.2f}x faster", 
                ha='center', va='center', fontsize=12)
    
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/caching_comparison.png')
    print("\nComparison chart saved to 'results/caching_comparison.png'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test caching performance")
    parser.add_argument("--iterations", type=int, default=5, help="Number of test iterations (unique keys)")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests per key")
    
    args = parser.parse_args()
    test_caching(args.iterations, args.requests)
