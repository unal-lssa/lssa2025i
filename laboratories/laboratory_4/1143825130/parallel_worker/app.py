# parallel_worker.py
# Servicio que ejecuta tareas pesadas en paralelo usando múltiples procesos.
# Ideal para cargas CPU-bound o procesos independientes.

import logging
import os
import time
from multiprocessing import Manager, Process, Queue, cpu_count

from flask import Flask, jsonify, request

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Cola compartida entre procesos
task_queue = Queue()

# Lista compartida
manager = Manager()
task_log = manager.list()

# Define cuántos procesos trabajadores se crearán (máximo 4 o núcleos disponibles)
NUM_PROCESSES = min(4, cpu_count())


# Función que procesa una tarea
def process_task(data):
    """
    Simula una tarea pesada que se ejecuta en un proceso separado.
    """
    print(f"[PID {os.getpid()}] Ejecutando tarea: {data}")
    logging.info(f"[PID {os.getpid()}] Ejecutando tarea: {data}")
    time.sleep(20)  # Simulación de cálculo o I/O costoso
    # Timestamp
    timestamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
    print(f"[PID {os.getpid()}] Tarea completada. {timestamp}")
    logging.info(f"[PID {os.getpid()}] Tarea completada. {timestamp}")


# Bucle principal de cada proceso
def worker_loop():
    """
    Cada proceso espera tareas en la cola y las ejecuta indefinidamente.
    """
    while True:
        try:
            task_data = task_queue.get()
            task_log.pop()
            if task_data is None:
                break  # Permitir detención limpia (opcional)
            process_task(task_data)
        except Exception as e:
            print(f"[PID {os.getpid()}] Error en tarea: {e}")
            logging.error(f"[PID {os.getpid()}] Error en tarea: {e}")


# Endpoint para enviar tareas a la cola
@app.route("/ptask", methods=["POST"])
def handle_heavy_task():
    """
    Recibe tareas via HTTP POST y las agrega a la cola para ejecución paralela.
    """
    data = request.json
    task_queue.put(data)
    task_log.append(data)
    return jsonify({'status': 'Tarea paralela encolada'}), 202


# Endpoint para obtener el total de tareas en paralelo
@app.route("/tasks", methods=["GET"])
def get_tasks():
    """
    Retorna el total de tareas en paralelo
    """
    return jsonify({'tasks': len(list(task_log))}), 200


if __name__ == "__main__":
    # Lanza los procesos trabajadores
    print(f"🔧 Iniciando {NUM_PROCESSES} procesos...")
    for _ in range(NUM_PROCESSES):
        p = Process(target=worker_loop, daemon=True)
        p.start()

    # Expone el servicio REST para recibir tareas
    app.run(host="0.0.0.0", port=5006, debug=True)
