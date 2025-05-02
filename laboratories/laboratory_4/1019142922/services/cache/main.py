"""Simple in memory Cache"""

from fastapi import FastAPI, HTTPException, status

app = FastAPI()
cache = {}


@app.get("/get/{key}")
async def get_cache(key: str):
    try:
        return {"value": cache[key]["value"]}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Value '{key}' was not found in cache",
        ) from e


@app.post("/set/{key}")
async def set_cache(key: str, value: dict):
    cache[key] = value
    return {"status": "ok"}
