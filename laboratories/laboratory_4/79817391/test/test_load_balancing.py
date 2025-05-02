import requests
import os
from concurrent.futures import ThreadPoolExecutor

from logger import setup_logger

# Configurar el logger
logger = setup_logger("Test load balancer", "test_load_balancer.log")


LOAD_BALANCER_URL = os.getenv("LOAD_BALANCER_URL", "http://127.0.0.1:8000")

def test_load_balancer():
   """
   Prueba el balanceo de carga enviando múltiples solicitudes.

   Este test verifica que un balanceador de carga distribuya correctamente las solicitudes
   entre los servidores disponibles. Se utiliza un conjunto de solicitudes concurrentes
   para evaluar el comportamiento del balanceador.

   Pasos del código:
   1. Define la URL del balanceador de carga utilizando la constante `LOAD_BALANCER_URL`.
   2. Crea un `ThreadPoolExecutor` con un máximo de 10 hilos para manejar solicitudes concurrentes.
   3. Utiliza `executor.map` para enviar 20 solicitudes HTTP GET a la URL del balanceador.
      Cada solicitud es manejada por un hilo del pool.
   4. Almacena las respuestas en una lista llamada `responses`.
   5. Verifica que todas las respuestas tengan un código de estado HTTP 200, lo que indica
      que todas las solicitudes fueron procesadas correctamente.
   6. Registra la información de las respuestas en el logger.
   """
   
   print_titulo()
   url = f"{LOAD_BALANCER_URL}/data"
   logger.info("Iniciando la prueba de balanceo de carga")
   logger.info(f"URL del balanceador de carga: {url}")
   with ThreadPoolExecutor(max_workers=10) as executor:
      responses = list(executor.map(lambda _: requests.get(url), range(20)))
      logger.info("Solicitudes enviadas al balanceador de carga")
      for resp in responses:
         api_gateway = ""
         if "5000" in resp.url:
             api_gateway = "Servidor: [ API Gateway 1 ]"
         else:
             api_gateway = "Servidor: [ API Gateway 2 ]"
             
         logger.info(f"Respuesta: {resp.status_code}, URL: {resp.url}, {api_gateway}")

   assert all(resp.status_code == 200 for resp in responses)
   
   
def print_titulo():
   frame = "=" * 75
   logger.info(f"""
{frame}

>> Este test prueba el balanceo de carga enviando múltiples solicitudes.
   
   Por lo tanto, se verifica que el [ balanceador de carga ] distribuya correctamente
   las solicitudes entre los diferentes API Gateway que se esta ejecutando por los 
   puertos 5000 y 5003 respectivamente.
   
   Para este ejercicio se realizá 20 solicitudes 10 serán atendidas por el 
   [ API Gateway 1 ] que corre por el puerto 5000  y 10 por el [ API Gateway 2 ]
   que corre por el puerto 5003.
   
   Pasos del código:
   
   1. Define la URL del balanceador de carga utilizando la constante `LOAD_BALANCER_URL`.
   2. Crea un `ThreadPoolExecutor` con un máximo de 10 hilos para manejar solicitudes concurrentes.
   3. Utiliza `executor.map` para enviar 20 solicitudes HTTP GET a la URL del balanceador.
     Cada solicitud es manejada por un hilo del pool.
   4. Almacena las respuestas en una lista llamada `responses`.
   5. Verifica que todas las respuestas tengan un código de estado HTTP 200, lo que indica
     que todas las solicitudes fueron procesadas correctamente.
   6. Registra la información de las respuestas en el logger.
   
   Se están utilizando assert para verificar el comportamiento esperado de las respuestas.
   7. Si la condición evaluada es False, lanza una excepción del tipo AssertionError.
{frame}
   """)




if __name__ == "__main__":
   test_load_balancer()