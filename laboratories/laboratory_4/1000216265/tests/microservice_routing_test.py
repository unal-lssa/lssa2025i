import requests
import threading
import time
import matplotlib.pyplot as plt
import argparse
import os
from collections import Counter

def get_token():
    """Get an authentication token from the API Gateway"""
    try:
        response = requests.get("http://localhost:8000/token")
        return response.json().get('token')
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

def test_microservice_routing(num_requests=50, concurrency=5):
    """Test routing across multiple microservice instances"""
    token = get_token()
    if not token:
        print("Failed to get authentication token")
        return
    
    print(f"Running microservice routing test with {num_requests} requests and concurrency {concurrency}")
    headers = {"Authorization": token}
    
    service_ids = []
    response_times = []
    errors = 0
    
    def make_request():
        nonlocal errors
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/process", headers=headers)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                service_id = data.get('service_id', 'unknown')
                service_ids.append(service_id)
                response_times.append(end_time - start_time)
                print(f"Request processed by microservice: {service_id}, took {end_time-start_time:.4f}s")
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
    service_distribution = dict(Counter(service_ids))
    
    print("\n===== RESULTS =====")
    print(f"Total Requests: {num_requests}")
    print(f"Successful Requests: {num_requests - errors}")
    print(f"Errors: {errors}")
    
    if response_times:
        print(f"Average Response Time: {sum(response_times) / len(response_times):.4f}s")
    
    print("\nMicroservice Distribution:")
    for service, count in service_distribution.items():
        print(f"  Service {service}: {count} requests ({count/len(service_ids)*100:.1f}%)")
    
    # Plot distribution
    plt.figure(figsize=(10, 6))
    plt.bar(service_distribution.keys(), service_distribution.values())
    plt.title('Request Distribution Across Microservices')
    plt.xlabel('Microservice ID')
    plt.ylabel('Number of Requests')
    plt.grid(axis='y', alpha=0.3)
    
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/microservice_distribution.png')
    print("\nDistribution chart saved to 'results/microservice_distribution.png'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test routing across multiple microservice instances")
    parser.add_argument("--requests", type=int, default=50, help="Number of requests to make")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent requests")
    
    args = parser.parse_args()
    test_microservice_routing(args.requests, args.concurrency)
