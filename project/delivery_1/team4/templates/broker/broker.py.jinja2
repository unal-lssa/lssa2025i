import asyncio
import websockets
import sqlite3
import json
import time

# Setup SQLite database
conn = sqlite3.connect("broker.db", check_same_thread=False)
cursor = conn.cursor()

# Tables
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER,
    subscriber_id TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics (id)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER,
    message TEXT,
    timestamp REAL,
    FOREIGN KEY (topic_id) REFERENCES topics (id)
)
"""
)

conn.commit()

# In-memory mapping: subscriber_id -> websocket connection
clients = {}


# Functions to manage broker
def create_topic(topic_name):
    try:
        cursor.execute("INSERT INTO topics (name) VALUES (?)", (topic_name,))
        conn.commit()
        print(f"Topic '{topic_name}' created.")
        return True
    except sqlite3.IntegrityError:
        print(f"Topic '{topic_name}' already exists.")
        return False


def subscribe(topic_name, subscriber_id):
    cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
    topic = cursor.fetchone()
    if not topic:
        print(f"Topic '{topic_name}' does not exist.")
        return False
    topic_id = topic[0]
    cursor.execute(
        "INSERT INTO subscriptions (topic_id, subscriber_id) VALUES (?, ?)",
        (topic_id, subscriber_id),
    )
    conn.commit()
    print(f"Subscriber '{subscriber_id}' subscribed to '{topic_name}'.")
    return True


def publish(topic_name, message):
    cursor.execute("SELECT id FROM topics WHERE name = ?", (topic_name,))
    topic = cursor.fetchone()
    if not topic:
        print(f"Topic '{topic_name}' does not exist.")
        return []

    topic_id = topic[0]
    timestamp = time.time()
    cursor.execute(
        "INSERT INTO messages (topic_id, message, timestamp) VALUES (?, ?, ?)",
        (topic_id, message, timestamp),
    )
    conn.commit()

    # Fetch subscribers
    cursor.execute(
        "SELECT subscriber_id FROM subscriptions WHERE topic_id = ?", (topic_id,)
    )
    subscribers = cursor.fetchall()
    return [sub[0] for sub in subscribers]


# WebSocket server logic
async def handler(websocket, path):
    try:
        # First, expect the client to send its ID
        raw_init = await websocket.recv()
        init_data = json.loads(raw_init)
        subscriber_id = init_data.get("subscriber_id")
        if not subscriber_id:
            await websocket.send(
                json.dumps({"error": "Missing subscriber_id on connect"})
            )
            return

        clients[subscriber_id] = websocket
        print(f"Client '{subscriber_id}' connected.")

        # Listen for commands
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action")

                if action == "create_topic":
                    topic_name = data.get("topic")
                    if create_topic(topic_name):
                        await websocket.send(
                            json.dumps({"status": "Topic created", "topic": topic_name})
                        )
                    else:
                        await websocket.send(
                            json.dumps(
                                {"status": "Topic already exists", "topic": topic_name}
                            )
                        )

                elif action == "subscribe":
                    topic_name = data.get("topic")
                    if subscribe(topic_name, subscriber_id):
                        await websocket.send(
                            json.dumps({"status": "Subscribed", "topic": topic_name})
                        )
                    else:
                        await websocket.send(
                            json.dumps(
                                {"error": "Subscription failed", "topic": topic_name}
                            )
                        )

                elif action == "publish":
                    topic_name = data.get("topic")
                    message_payload = json.dumps(data.get("message"))
                    subscribers = publish(topic_name, message_payload)
                    for sub_id in subscribers:
                        if sub_id in clients:
                            await clients[sub_id].send(
                                json.dumps(
                                    {
                                        "topic": topic_name,
                                        "message": json.loads(message_payload),
                                    }
                                )
                            )

                else:
                    await websocket.send(json.dumps({"error": "Unknown action"}))
            except Exception as e:
                await websocket.send(json.dumps({"error": str(e)}))

    except websockets.exceptions.ConnectionClosed:
        print(f"Client '{subscriber_id}' disconnected.")
    finally:
        if subscriber_id in clients:
            del clients[subscriber_id]


# Start the WebSocket server
async def main():
    async with websockets.serve(handler, "localhost", 6789):
        print("Broker Server running on ws://localhost:6789")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
