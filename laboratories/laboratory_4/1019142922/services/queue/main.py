"""Naive implementation of an in-memory Task Queue"""
from queue import Queue

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
task_queue = Queue()

class Task(BaseModel):
    task_type: str
    payload: dict

@app.post("/enqueue")
async def enqueue(task: Task):
    task_queue.put(task.model_dump())
    return {"status": "task enqueued"}

@app.get("/dequeue")
async def dequeue() -> Task:
    if task_queue.empty():
        raise HTTPException(status_code=404, detail="No tasks in the queue")
    task = task_queue.get()
    return task

