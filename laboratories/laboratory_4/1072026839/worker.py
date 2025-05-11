from flask import Flask, request, jsonify
import threading
import time
import uuid

app = Flask(__name__)
instance_id = str(uuid.uuid4())[:8] # ID único

@app.route("/task", methods=["POST"])
def handle_task():
    data = request.json
    thread = threading.Thread(target=process_task, args=(data,))
    thread.start()
    
    return jsonify({
        'status': 'Started',
        'worker_instance': instance_id
    }), 202

def process_task(data):
    print(f"Worker {instance_id} procesando tarea: {data}")
    time.sleep(5) # Simular procesamiento
    print(f"Worker {instance_id} completó tarea: {data}")

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5005
    print(f"Worker iniciando en puerto {port} (Instance ID: {instance_id})")
    app.run(port=port, debug=True)