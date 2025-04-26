import requests

BASE_URL = "http://127.0.0.1:5000"
CLIENTS_URL = f"{BASE_URL}/clients"
ADMIN_URL = f"{BASE_URL}/admin"
LOGIN_URL = f"{BASE_URL}/login"
EXPIRED_URL = f"{BASE_URL}/expired-token"

def get_token(username, password):
    try:
        response = requests.post(LOGIN_URL, json={"username": username, "password": password})
        response.raise_for_status()
        token = response.json()["token"]
        return f"Bearer {token}"
    except Exception as e:
        print(f"Failed to get token for {username}: {e}")
        return ""

def get_expired_token(username, password):
    try:
        response = requests.post(EXPIRED_URL, json={"username": username, "password": password})
        response.raise_for_status()
        token = response.json()["expired_token"]
        return f"Bearer {token}"
    except Exception as e:
        print(f"Failed to get expired token: {e}")
        return ""

def test_endpoint(label, url, token=None):
    print(f"\n[{label}] {url}")
    headers = {"Authorization": token} if token else {}
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        print("Response:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print("Request failed.")
        if e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print("Response:")
            print(e.response.text)

def main():
    print("Getting tokens...")
    user1_token = get_token("user1", "password123")
    user2_token = get_token("user2", "password456")
    admin_token = get_token("admin", "adminpass")
    expired_token = get_expired_token("user1", "password123")

    # Test cases
    test_endpoint("User1 -> /clients", CLIENTS_URL, user1_token)
    test_endpoint("User2 -> /clients", CLIENTS_URL, user2_token)
    test_endpoint("Admin -> /clients", CLIENTS_URL, admin_token)
    test_endpoint("User1 -> /admin", ADMIN_URL, user1_token)
    test_endpoint("Admin -> /admin", ADMIN_URL, admin_token)
    test_endpoint("Expired Token -> /clients", CLIENTS_URL, expired_token)
    test_endpoint("No Token -> /clients", CLIENTS_URL)

if __name__ == "__main__":
    main()
