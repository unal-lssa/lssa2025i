import asyncio
import aiohttp
import time

BASE_URL = "http://127.0.0.1:5000"  # Updated to match your Postman URL
USERNAME = "user1"
PASSWORD = "password123"
TOTAL_REQUESTS = 100
CONCURRENT = 10
TEST_DATA_ENDPOINT = True  # Set to True to test /data endpoint

sem = asyncio.Semaphore(CONCURRENT)

async def get_token(session):
    url = f"{BASE_URL}/login"
    async with session.post(url, json={"username": USERNAME, "password": PASSWORD}) as resp:
        data = await resp.json()
        return data.get("token")

async def send_request(session, token, i):
    headers = {"Authorization": f"{token}"}  # Correct format of the Authorization header
    url = f"{BASE_URL}/data" if TEST_DATA_ENDPOINT else f"{BASE_URL}/longtask"
    
    async with sem:
        try:
            async with session.get(url, headers=headers) as resp:  # Use GET for /data
                status = resp.status
                response_body = await resp.json()  # Read the response body if needed
                print(f"Request {i}: Status {status}, Response: {response_body}")
        except Exception as e:
            print(f"Request {i}: Failed with error {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        token = await get_token(session)
        if not token:
            print("Could not get token.")
            return
        print(f"Authentication successful. Token: {token}")
        
        tasks = [send_request(session, token, i) for i in range(TOTAL_REQUESTS)]
        start_time = time.time()
        await asyncio.gather(*tasks)
        duration = time.time() - start_time
        print(f"All requests completed in {duration:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())
