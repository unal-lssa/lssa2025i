import requests
import time
import sys

def test_rate_limit(token, endpoint, requests_count):
    headers = {"Authorization": f"Bearer {token}"}
    success = 0
    rate_limited = 0
    
    print(f"Sending {requests_count} rapid requests...")
    for i in range(requests_count):
        response = requests.get(f"http://localhost:5000/{endpoint}", headers=headers)
        if response.status_code == 200:
            success += 1
        elif response.status_code == 429:  # Rate limit exceeded
            rate_limited += 1
            print(f"Rate limit reached after {success} requests")
            break
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
    
    print(f"Results: {success} successful requests, {rate_limited} rate limited")
    return success, rate_limited

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python rate_limit_test.py <token> <role>")
        sys.exit(1)
    
    token = sys.argv[1]
    role = sys.argv[2].upper()
    
    # Test rate limits based on role
    if role == "ADMIN":
        print("Testing rate limits for ADMIN role (limit: 100 req/min)")
        test_rate_limit(token, "products", 105)
    else:
        print("Testing rate limits for USER role (limit: 10 req/min)")
        test_rate_limit(token, "products", 15)