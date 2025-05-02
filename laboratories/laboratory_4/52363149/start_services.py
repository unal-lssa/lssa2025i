import subprocess
import time


# Función para ejecutar un comando en un proceso separado
def run_command(command):
    return subprocess.Popen(command, shell=True)


# Iniciar los microservicios
print("Iniciando microservicios...")

# Iniciar microservicio 1
microservice1 = run_command("python microservice.py")
time.sleep(2)  # Esperar 2 segundos para asegurar que se haya iniciado correctamente

# Iniciar microservicio 2
microservice2 = run_command("python microservice2.py")
time.sleep(2)

# Iniciar el servicio de análisis
analytics_service = run_command("python analytics_service.py")
time.sleep(2)

# Iniciar el servicio de worker
worker_service = run_command("python worker.py")
time.sleep(2)

# Iniciar el servicio de caché
cache_service = run_command("python cache.py")
time.sleep(2)

# Iniciar la base de datos
db_service = run_command("python database.py")
time.sleep(2)

# Iniciar el balanceador de carga
load_balancer = run_command("python load_balancer.py")
time.sleep(2)

# Iniciar el api_gateway
api_gateway= run_command("python api_gateway.py")
time.sleep(2)

print("Todos los servicios se han iniciado exitosamente.")

# Esperar que el script se cierre cuando el usuario lo decida
try:
    while True:
        time.sleep(100)  # Mantener el script en ejecución
except KeyboardInterrupt:
    print("Interrumpido por el usuario. Deteniendo los servicios...")

    # Detener todos los servicios
    microservice1.terminate()
    microservice2.terminate()
    analytics_service.terminate()
    cache_service.terminate()
    worker_service.terminate()
    db_service.terminate()
    load_balancer.terminate()
    api_gateway.terminate()

    print("Servicios detenidos.")
