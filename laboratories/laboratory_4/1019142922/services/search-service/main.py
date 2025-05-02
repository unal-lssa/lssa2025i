"""Search tutors microservice"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
import asyncpg

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await asyncpg.create_pool(
        user="user", password="password", database="tutoring", host="database"
    )

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/search")
async def search_tutors(subject: str):
    async with app.state.db.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM tutors WHERE subject = $1", subject)
        return [dict(row) for row in rows]

