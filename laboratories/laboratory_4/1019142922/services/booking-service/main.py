"""Search tutors microservice"""

from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, Body
import asyncpg
import httpx


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await asyncpg.create_pool(
        user="user", password="password", database="tutoring", host="database"
    )

    yield


app = FastAPI(lifespan=lifespan)


async def send_notification(student_id: int, tutor_id: int):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://queue:8000/enqueue",
            json={
                "task_type": "notification",
                "payload": {
                    "student_id": student_id,
                    "tutor_id": tutor_id,
                    "type": "Booking",
                },
            },
        )


@app.post("/book")
async def book_session(
    student_id: Annotated[int, Body()],
    tutor_id: Annotated[int, Body()],
    background_tasks: BackgroundTasks,
):
    async with app.state.db.acquire() as conn:
        await conn.execute(
            "INSERT INTO bookings (student_id, tutor_id, time) VALUES ($1, $2, NOW())",
            student_id,
            tutor_id,
        )

    background_tasks.add_task(send_notification, student_id, tutor_id)

    return {"status": "success"}
