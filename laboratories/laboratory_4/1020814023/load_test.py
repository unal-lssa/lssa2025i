import asyncio
import aiohttp
import time

USERNAME = "user1"
PASSWORD = "password123"
TOTAL_REQUESTS = 100
CONCURRENT = 10

sem = asyncio.Semaphore(CONCURRENT)

async def get_token(session):
    url = "http://127.0.0.1:8000/login"
    async with session.post(url, json={"username": USERNAME, "password": PASSWORD}) as resp:
        data = await resp.json()
        return data.get("token")

async def send_data_request(session, token, i):
    headers = {"Authorization": f"{token}"}
    url = "http://127.0.0.1:8000/data"

    async with sem:
        try:
            async with session.get(url, headers=headers) as resp:
                status = resp.status
                response_body = await resp.json()
                print(f"[DATA] Request {i}: Status {status}, Response: {response_body}")
        except Exception as e:
            print(f"[DATA] Request {i}: Failed with error {e}")

async def send_longtask_request(session, token, i):
    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json"
    }
    url = "http://127.0.0.1:8000/longtask"
    payload = {"task": "report"}

    async with sem:
        try:
            async with session.post(url, headers=headers, json={}) as resp:
                status = resp.status
                response_body = await resp.json()
                print(f"[LONGTASK] Request {i}: Status {status}, Response: {response_body}")
        except Exception as e:
            print(f"[LONGTASK] Request {i}: Failed with error {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        
        # Autenticación con token
        token = await get_token(session)
        if not token:
            print("No fue posible obtener el token.")
            return
        print(f"Autenticación Satisfactoria. Token: {token}")

        # Simulación de solicitudes
        tasks = []
        # 50 solicitidues /data
        tasks += [send_data_request(session, token, i) for i in range(1, 51)]
        # 50 solicitudes /longtask
        tasks += [send_longtask_request(session, token, i) for i in range(51, 101)]

        # Resumen del tiempo de ejecución de las pruebas
        start_time = time.time()
        await asyncio.gather(*tasks)
        duration = time.time() - start_time
        print(f"Todas las solicitudes completadas en {duration:.2f} segundos.")

if __name__ == "__main__":
    asyncio.run(main())
