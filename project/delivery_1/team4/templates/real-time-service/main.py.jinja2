import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import redis.asyncio as redis

app = FastAPI()
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

connections: set[WebSocket] = set()

async def redis_listener(pubsub):
    async for message in pubsub.listen():
        # Sólo procesar mensajes tipo 'message'
        if message["type"] == "message":
            data = message["data"]
            if isinstance(data, bytes):
                data = data.decode()
            # reenviar a todos los WebSockets
            to_remove = []
            for ws in connections:
                try:
                    await ws.send_text(data)
                except WebSocketDisconnect:
                    to_remove.append(ws)
            for ws in to_remove:
                connections.remove(ws)

@app.on_event("startup")
async def startup():
    # Cliente Redis y PubSub
    app.state.redis = redis.from_url(REDIS_URL)
    app.state.pubsub = app.state.redis.pubsub(ignore_subscribe_messages=True)
    await app.state.pubsub.subscribe("chat")
    asyncio.create_task(redis_listener(app.state.pubsub))

@app.on_event("shutdown")
async def shutdown():
    await app.state.pubsub.unsubscribe("chat")
    await app.state.redis.close()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.add(ws)
    try:
        while True:
            msg = await ws.receive_text()
            # Publicar en Redis
            await app.state.redis.publish("chat", msg)
    except WebSocketDisconnect:
        connections.remove(ws)
