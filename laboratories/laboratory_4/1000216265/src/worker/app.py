from flask import Flask, request, jsonify
import threading
import time
import os

app = Flask(__name__)

# Environment variables
PORT = int(os.environ.get("FLASK_PORT", 5005))

# Task queue
task_queue = []
task_results = {}
task_counter = 0
lock = threading.Lock()

@app.route("/task", methods=["POST"])
def handle_task():
    global task_counter
    
    with lock:
        task_id = str(task_counter)
        task_counter += 1
        
    data = request.json
    task_queue.append((task_id, data))
    
    # Start processing in background
    thread = threading.Thread(target=process_task, args=(task_id, data))
    thread.start()
    
    return jsonify({
        'status': 'Started',
        'task_id': task_id
    }), 202

@app.route("/task/<task_id>", methods=["GET"])
def get_task_status(task_id):
    if task_id in task_results:
        return jsonify({
            'status': 'completed',
            'result': task_results[task_id]
        })
    
    for id, _ in task_queue:
        if id == task_id:
            return jsonify({'status': 'processing'})
    
    return jsonify({'status': 'not_found'}), 404

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify({
        'queue_length': len(task_queue),
        'completed_tasks': len(task_results)
    })

def process_task(task_id, data):
    print(f"Processing task {task_id}: {data}")
    
    # Simulate long-running task
    processing_time = 5  # seconds
    time.sleep(processing_time)
    
    # Store result
    result = {
        'processed_at': time.time(),
        'original_data': data,
        'result': f"Task {task_id} completed successfully"
    }
    
    task_results[task_id] = result
    print(f"Task {task_id} complete")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        'status': 'up',
        'queue_length': len(task_queue),
        'completed_tasks': len(task_results)
    })

if __name__ == "__main__":
    print(f"Worker service starting on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
