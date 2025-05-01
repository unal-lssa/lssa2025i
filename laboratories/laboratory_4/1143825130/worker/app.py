# worker.py
# Servicio que recibe tareas asíncronas y las procesa en segundo plano usando hilos.

import logging
import threading
import time
from queue import Queue

from flask import Flask, jsonify, request

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Cola de tareas compartida entre los hilos
task_queue = Queue()

# Número de hilos simultáneos (configurable)
NUM_WORKERS = 4


# Función que procesa una tarea
def process_task(data):
    """
    Simula una operación costosa (bloqueante).
    Esta función se ejecuta en un hilo del pool.
    """
    print(f"[{threading.current_thread().name}] Procesando tarea: {data}")
    logging.info(f"[{threading.current_thread().name}] Procesando tarea: {data}")
    time.sleep(10)  # Simula un trabajo que toma tiempo
    # Timestamp
    timestamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
    print(f"[{threading.current_thread().name}] Tarea completada {timestamp}")
    logging.info(f"[{threading.current_thread().name}] Tarea completada {timestamp}")


# Bucle principal de cada hilo trabajador
def worker_loop():
    """
    Bucle principal de cada hilo trabajador.
    Escucha la cola y procesa tareas indefinidamente.
    """
    while True:
        task_data = task_queue.get()
        if task_data is None:
            break
        process_task(task_data)
        task_queue.task_done()


# Inicialización del pool de hilos
for i in range(NUM_WORKERS):
    thread = threading.Thread(target=worker_loop, daemon=True, name=f"Worker-{i+1}")
    thread.start()


# Endpoint para enviar tareas a la cola
@app.route("/task", methods=["POST"])
def handle_task():
    """
    Endpoint que recibe tareas y las agrega a la cola para procesamiento.
    """
    data = request.json
    task_queue.put(data)
    return jsonify({'status': 'Tarea encolada'}), 202


# Endpoint para obtener el total de tareas en la cola
@app.route("/tasks", methods=["GET"])
def get_tasks():
    """
    Retorna el total de tareas en la cola.
    """
    # Acceso seguro a la lista de tareas sin modificar la cola
    with task_queue.mutex:
        tareas_en_cola = list(task_queue.queue)
    return jsonify({'tasks': len(tareas_en_cola)}), 200


if __name__ == "__main__":
    # El servicio escucha en el puerto 5005 (coincide con docker-compose)
    app.run(host="0.0.0.0", port=5005, debug=True)
