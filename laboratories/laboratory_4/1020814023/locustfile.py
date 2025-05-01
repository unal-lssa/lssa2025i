import asyncio
import aiohttp
import time

BASE_URL = "http://localhost:8000"
USERNAME = "user1"
PASSWORD = "password123"
TOTAL_REQUESTS = 100
CONCURRENT = 10
TEST_DATA_ENDPOINT = True  # Set to False to test /longtask instead

sem = asyncio.Semaphore(CONCURRENT)

async def get_token(session):
    url = f"{BASE_URL}/login"
    async with session.post(url, json={"username": USERNAME, "password": PASSWORD}) as resp:
        data = await resp.json()
        return data.get("token")

async def send_request(session, token, i):
    headers = {"Authorization": token}
    url = f"{BASE_URL}/data" if TEST_DATA_ENDPOINT else f"{BASE_URL}/longtask"
    method = session.get if TEST_DATA_ENDPOINT else session.post
    payload = None if TEST_DATA_ENDPOINT else {"task_id": i, "payload": "some data"}

    async with sem:
        try:
            async with method(url, headers=headers, json=payload) as resp:
                status = resp.status
                print(f"Request {i}: Status {status}")
        except Exception as e:
            print(f"Request {i}: Failed with error {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        token = await get_token(session)
        if not token:
            print("Could not get token.")
            return
        token = f"Bearer {token}"
        tasks = [send_request(session, token, i) for i in range(TOTAL_REQUESTS)]
        start_time = time.time()
        await asyncio.gather(*tasks)
        duration = time.time() - start_time
        print(f"All requests completed in {duration:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())

