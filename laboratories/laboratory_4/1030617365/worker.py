from flask import Flask, request, jsonify
import threading
import time
import uuid
import requests
import queue
import json
    
app = Flask(__name__)

# Cola de tareas y registro
task_queue = queue.Queue()
tasks = {}  # Seguimiento de tareas {task_id: {status, data, result}}
task_lock = threading.Lock()

# Constantes
MAX_WORKERS = 4  # Número máximo de workers concurrentes
TASK_TIMEOUT = 120  # Timeout en segundos para tareas

# Iniciar workers
active_workers = 0
worker_lock = threading.Lock()

def worker_thread():
    global active_workers
    
    with worker_lock:
        active_workers += 1
    
    try:
        while True:
            try:
                # Intentar obtener una tarea con timeout
                # (para permitir que el worker termine si es necesario)
                try:
                    task_id, task_data = task_queue.get(timeout=5)
                except queue.Empty:
                    continue
                
                # Actualizar estado de la tarea
                with task_lock:
                    if task_id in tasks:
                        tasks[task_id]["status"] = "processing"
                
                # Registrar inicio de procesamiento
                print(f"[Worker] Procesando tarea {task_id}: {task_data}")
                
                # Simulación de trabajo (diferente según el tipo de tarea)
                task_type = task_data.get("type", "default")
                result = None
                
                try:
                    if task_type == "report":
                        # Tarea larga: generar informe
                        time.sleep(5)
                        result = {
                            "report_data": f"Informe generado para {task_data.get('parameters', {})}",
                            "timestamp": time.time()
                        }
                    elif task_type == "notification":
                        # Tarea rápida: enviar notificación
                        time.sleep(1)
                        result = {
                            "notification_sent": True,
                            "recipient": task_data.get("recipient", "unknown")
                        }
                    elif task_type == "error_test":
                        # Tarea para probar el manejo de errores
                        raise Exception("Error de prueba deliberado")
                    else:
                        # Tarea genérica
                        time.sleep(3)
                        result = {
                            "processed": True,
                            "input_data": task_data
                        }
                        
                    # Actualizar estado de la tarea como completada
                    with task_lock:
                        if task_id in tasks:
                            tasks[task_id]["status"] = "completed"
                            tasks[task_id]["result"] = result
                            tasks[task_id]["completed_at"] = time.time()
                    
                    # Notificar al sistema de monitoreo
                    try:
                        requests.post("http://127.0.0.1:5006/metrics/update", 
                                     json={"task_completed": True},
                                     timeout=0.5)
                    except:
                        pass
                        
                except Exception as e:
                    # Marcar la tarea como fallida
                    with task_lock:
                        if task_id in tasks:
                            tasks[task_id]["status"] = "failed"
                            tasks[task_id]["error"] = str(e)
                            tasks[task_id]["completed_at"] = time.time()
                    
                    print(f"[Worker] Error al procesar tarea {task_id}: {e}")
                
                # Marcar la tarea como completada en la cola
                task_queue.task_done()
                
            except Exception as e:
                print(f"[Worker] Error inesperado: {e}")
                # Breve pausa antes de intentar procesar la siguiente tarea
                time.sleep(1)
    finally:
        # Reducir contador de workers activos al terminar
        with worker_lock:
            active_workers -= 1

# Iniciar el pool de workers
def start_worker_pool():
    for _ in range(MAX_WORKERS):
        t = threading.Thread(target=worker_thread, daemon=True)
        t.start()

# Endpoint para encolar nuevas tareas
@app.route("/task", methods=["POST"])
def handle_task():
    data = request.json
    
    # Generar ID único para la tarea
    task_id = str(uuid.uuid4())
    
    # Registrar tarea
    with task_lock:
        tasks[task_id] = {
            "status": "queued",
            "data": data,
            "created_at": time.time(),
            "result": None
        }
    
    # Encolar tarea
    task_queue.put((task_id, data))
    
    return jsonify({
        "status": "queued",
        "task_id": task_id
    }), 202

# Endpoint para consultar estado de una tarea
@app.route("/task/<task_id>", methods=["GET"])
def get_task_status(task_id):
    with task_lock:
        if task_id in tasks:
            return jsonify(tasks[task_id])
        else:
            return jsonify({"error": "Tarea no encontrada"}), 404

# Endpoint para obtener lista de tareas
@app.route("/tasks", methods=["GET"])
def list_tasks():
    status_filter = request.args.get("status", None)
    
    with task_lock:
        if status_filter:
            filtered_tasks = {
                task_id: task_data 
                for task_id, task_data in tasks.items() 
                if task_data["status"] == status_filter
            }
            return jsonify({"tasks": filtered_tasks})
        else:
            return jsonify({"tasks": tasks})

# Endpoint para health checks
@app.route("/health", methods=["GET"])
def health():
    with worker_lock:
        worker_count = active_workers
    
    return jsonify({
        "status": "ok",
        "queue_size": task_queue.qsize(),
        "active_workers": worker_count,
        "max_workers": MAX_WORKERS
    })

# Limpieza de tareas antiguas
def cleanup_old_tasks():
    while True:
        now = time.time()
        with task_lock:
            # Identificar tareas completadas o fallidas que son antiguas
            task_ids_to_remove = [
                task_id for task_id, task_data in tasks.items()
                if (task_data["status"] in ["completed", "failed"] and
                    "completed_at" in task_data and
                    now - task_data["completed_at"] > 3600)  # 1 hora
            ]
            
            # Eliminar tareas antiguas
            for task_id in task_ids_to_remove:
                del tasks[task_id]
        
        # Esperar antes de la próxima limpieza
        time.sleep(300)  # 5 minutos

if __name__ == "__main__":
    # Iniciar pool de workers
    start_worker_pool()
    
    # Iniciar thread de limpieza
    cleanup_thread = threading.Thread(target=cleanup_old_tasks, daemon=True)
    cleanup_thread.start()
    
    # Iniciar servidor Flask
    app.run(port=5005, debug=True, threaded=True)