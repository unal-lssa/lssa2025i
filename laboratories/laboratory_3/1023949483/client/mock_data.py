# Add role property to users
USERS = {
    "user1": {"password": "password123", "role": "user"},
    "user2": {"password": "password456", "role": "user"},
    "admin": {"password": "adminpass", "role": "admin"}
}

# Mocked client data
CLIENTS = [
    {"id": 1, "name": "Alice", "owner": "user1"},
    {"id": 2, "name": "Bob", "owner": "user2"},
    {"id": 3, "name": "Charlie", "owner": "user1"}
]