from flask import Flask, jsonify, request
import requests
import threading
import time
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from collections import Counter

app = Flask(__name__)

# Test results storage
results = {
    'load_balancing': {},
    'caching': {},
}

# Get token for authenticated requests
def get_token():
    try:
        response = requests.get("http://load_balancer:8000/token")
        return response.json().get('token')
    except:
        return None

# Run load balancing test
def test_load_balancing(num_requests=100, concurrency=10):
    token = get_token()
    if not token:
        return {"error": "Failed to get authentication token"}

    headers = {"Authorization": token}
    
    gateway_ids = []
    response_times = []
    errors = 0
    
    def make_request():
        try:
            start_time = time.time()
            response = requests.get("http://load_balancer:8000/data", headers=headers)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                gateway_ids.append(data.get('gateway_id', 'unknown'))
                response_times.append(end_time - start_time)
            else:
                errors += 1
        except:
            errors += 1
    
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
    
    # Analyze results
    gateway_distribution = dict(Counter(gateway_ids))
    
    # Chart data
    plt.figure(figsize=(10, 6))
    plt.bar(gateway_distribution.keys(), gateway_distribution.values())
    plt.title('Request Distribution Across API Gateways')
    plt.xlabel('Gateway ID')
    plt.ylabel('Number of Requests')
    plt.grid(axis='y', alpha=0.3)
    
    # Save chart to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # Prepare histogram data for response times
    hist, bins = np.histogram(response_times, bins=10)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    
    # Create response time histogram
    plt.figure(figsize=(10, 6))
    plt.bar(bin_centers, hist, width=bin_centers[1]-bin_centers[0])
    plt.title('Response Time Distribution')
    plt.xlabel('Response Time (s)')
    plt.ylabel('Number of Requests')
    plt.grid(axis='y', alpha=0.3)
    
    # Save histogram to buffer
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    histogram = base64.b64encode(buf2.read()).decode('utf-8')
    plt.close()
    
    return {
        "total_requests": num_requests,
        "successful_requests": num_requests - errors,
        "errors": errors,
        "gateway_distribution": gateway_distribution,
        "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
        "min_response_time": min(response_times) if response_times else 0,
        "max_response_time": max(response_times) if response_times else 0,
        "distribution_chart": chart,
        "response_time_histogram": histogram
    }

# Run caching performance test
def test_caching(iterations=5, requests_per_iteration=20):
    token = get_token()
    if not token:
        return {"error": "Failed to get authentication token"}

    headers = {"Authorization": token}
    
    # First, make sure cache is empty
    requests.post("http://load_balancer:8000/cache/flush")
    
    # Run test over several iterations
    cache_hit_times = []
    cache_miss_times = []
    
    for iteration in range(iterations):
        # Generate a unique cache key for this iteration
        key = f"test_key_{iteration}"
        
        # First request (cache miss)
        start_time = time.time()
        response = requests.get(f"http://load_balancer:8000/data?key={key}", headers=headers)
        miss_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if not data.get('cached', False):
                cache_miss_times.append(miss_time)
        
        # Subsequent requests (should be cache hits)
        hit_times = []
        for _ in range(requests_per_iteration - 1):
            start_time = time.time()
            response = requests.get(f"http://load_balancer:8000/data?key={key}", headers=headers)
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('cached', False):
                    hit_times.append(request_time)
        
        # Average hit time for this key
        if hit_times:
            cache_hit_times.append(sum(hit_times) / len(hit_times))
    
    # Create comparison chart
    avg_miss_time = sum(cache_miss_times) / len(cache_miss_times) if cache_miss_times else 0
    avg_hit_time = sum(cache_hit_times) / len(cache_hit_times) if cache_hit_times else 0
    
    plt.figure(figsize=(10, 6))
    plt.bar(['Cache Miss', 'Cache Hit'], [avg_miss_time, avg_hit_time])
    plt.title('Average Response Time: Cache Hit vs Miss')
    plt.ylabel('Time (s)')
    plt.grid(axis='y', alpha=0.3)
    
    # Save chart to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # Calculate speedup
    speedup = avg_miss_time / avg_hit_time if avg_hit_time > 0 else 0
    
    return {
        "iterations": iterations,
        "requests_per_iteration": requests_per_iteration,
        "avg_cache_miss_time": avg_miss_time,
        "avg_cache_hit_time": avg_hit_time,
        "speedup_factor": speedup,
        "comparison_chart": chart
    }

# Test endpoints
@app.route("/test/load-balancing", methods=["POST"])
def run_load_balancing_test():
    params = request.json or {}
    num_requests = params.get('num_requests', 100)
    concurrency = params.get('concurrency', 10)
    
    results['load_balancing'] = test_load_balancing(num_requests, concurrency)
    return jsonify(results['load_balancing'])

@app.route("/test/caching", methods=["POST"])
def run_caching_test():
    params = request.json or {}
    iterations = params.get('iterations', 5)
    requests_per_iteration = params.get('requests_per_iteration', 20)
    
    results['caching'] = test_caching(iterations, requests_per_iteration)
    return jsonify(results['caching'])

@app.route("/results", methods=["GET"])
def get_results():
    return jsonify(results)

@app.route("/", methods=["GET"])
def index():
    return """
    <html>
    <head>
        <title>Load Testing Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            button { padding: 10px; margin: 10px 0; background: #4CAF50; color: white; border: none; cursor: pointer; }
            button:hover { background: #45a049; }
            .results { margin-top: 20px; }
            img { max-width: 100%; height: auto; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Load Testing Dashboard</h1>
        
        <h2>Load Balancing Test</h2>
        <button onclick="runTest('load-balancing')">Run Load Balancing Test</button>
        <div id="loadBalancingResults" class="results"></div>
        
        <h2>Caching Test</h2>
        <button onclick="runTest('caching')">Run Caching Test</button>
        <div id="cachingResults" class="results"></div>
        
        <script>
            function runTest(testType) {
                const resultDiv = document.getElementById(testType === 'load-balancing' ? 'loadBalancingResults' : 'cachingResults');
                resultDiv.innerHTML = 'Running test...';
                
                fetch('/test/' + testType, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({})
                })
                .then(response => response.json())
                .then(data => {
                    let html = '<h3>Results:</h3>';
                    
                    if (testType === 'load-balancing') {
                        html += `<p>Total Requests: ${data.total_requests}</p>`;
                        html += `<p>Successful: ${data.successful_requests}</p>`;
                        html += `<p>Errors: ${data.errors}</p>`;
                        html += `<p>Average Response Time: ${data.avg_response_time.toFixed(3)}s</p>`;
                        html += `<h4>Gateway Distribution:</h4>`;
                        html += `<p>${JSON.stringify(data.gateway_distribution)}</p>`;
                        html += `<img src="data:image/png;base64,${data.distribution_chart}" alt="Distribution Chart">`;
                        html += `<img src="data:image/png;base64,${data.response_time_histogram}" alt="Response Time Histogram">`;
                    } else {
                        html += `<p>Avg Cache Miss Time: ${data.avg_cache_miss_time.toFixed(3)}s</p>`;
                        html += `<p>Avg Cache Hit Time: ${data.avg_cache_hit_time.toFixed(3)}s</p>`;
                        html += `<p>Speedup Factor: ${data.speedup_factor.toFixed(2)}x</p>`;
                        html += `<img src="data:image/png;base64,${data.comparison_chart}" alt="Cache Comparison Chart">`;
                    }
                    
                    resultDiv.innerHTML = html;
                })
                .catch(error => {
                    resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
                });
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("Load testing service starting")
    app.run(host="0.0.0.0", port=5050, debug=True)
