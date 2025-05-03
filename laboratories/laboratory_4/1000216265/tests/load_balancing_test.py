import requests
import threading
import time
import matplotlib.pyplot as plt
from collections import Counter
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


def test_load_balancing(num_requests=100, concurrency=10):
    """Test load balancing by making multiple concurrent requests and analyzing gateway distribution"""
    token = get_token()
    if not token:
        print("Failed to get authentication token")
        return
    
    print(f"Running load balancing test with {num_requests} requests and concurrency {concurrency}")
    headers = {"Authorization": token}
    
    gateway_ids = []
    response_times = []
    errors = 0
    
    def make_request():
        nonlocal errors
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/data", headers=headers)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                gateway_id = data.get('gateway_id', 'unknown')
                gateway_ids.append(gateway_id)
                response_times.append(end_time - start_time)
                print(f"Request processed by gateway: {gateway_id}, took {end_time-start_time:.4f}s")
            else:
                errors += 1
                print(f"Request failed with status code: {response.status_code}")
        except Exception as e:
            errors += 1
            print(f"Request error: {e}")
    
    # Create and start threads
    threads = []
    for _ in range(num_requests):
        t = threading.Thread(target=make_request)
        threads.append(t)
    
    # Start threads in batches for controlled concurrency
    for i in range(0, num_requests, concurrency):
        batch = threads[i:i+concurrency]
        for thread in batch:
            thread.start()
        for thread in batch:
            thread.join()
        print(f"Completed batch {i//concurrency + 1}/{(num_requests+concurrency-1)//concurrency}")
    
    # Analyze results
    gateway_distribution = dict(Counter(gateway_ids))
    
    print("\n===== RESULTS =====")
    print(f"Total Requests: {num_requests}")
    print(f"Successful Requests: {num_requests - errors}")
    print(f"Errors: {errors}")
    
    if response_times:
        print(f"Average Response Time: {sum(response_times) / len(response_times):.4f}s")
        print(f"Minimum Response Time: {min(response_times):.4f}s")
        print(f"Maximum Response Time: {max(response_times):.4f}s")
    
    print("\nGateway Distribution:")
    for gateway, count in gateway_distribution.items():
        print(f"  Gateway {gateway}: {count} requests ({count/len(gateway_ids)*100:.1f}%)")
    
    # Plot distribution
    plt.figure(figsize=(10, 6))
    plt.bar(gateway_distribution.keys(), gateway_distribution.values())
    plt.title('Request Distribution Across API Gateways')
    plt.xlabel('Gateway ID')
    plt.ylabel('Number of Requests')
    plt.grid(axis='y', alpha=0.3)
    
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/load_balancing_distribution.png')
    print("\nDistribution chart saved to 'results/load_balancing_distribution.png'")
    
    # Plot response time histogram
    plt.figure(figsize=(10, 6))
    plt.hist(response_times, bins=20)
    plt.title('Response Time Distribution')
    plt.xlabel('Response Time (s)')
    plt.ylabel('Number of Requests')
    plt.grid(axis='y', alpha=0.3)
    plt.savefig('results/load_balancing_response_times.png')
    print("Response time histogram saved to 'results/load_balancing_response_times.png'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test load balancing across API gateway instances")
    parser.add_argument("--requests", type=int, default=100, help="Number of requests to make")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent requests")
    
    args = parser.parse_args()
    test_load_balancing(args.requests, args.concurrency)
