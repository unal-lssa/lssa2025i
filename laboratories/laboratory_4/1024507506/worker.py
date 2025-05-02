from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

@app.route("/task", methods=["POST"])
def handle_task():
    data = request.json
    thread = threading.Thread(target=process_task, args=(data,))
    thread.start()
    return jsonify({'status': 'Started'}), 202

tasks_processed = 0

def process_task(data):
    global tasks_processed
    print(f"Processing task: {data}")
    time.sleep(5)  # Simulate delay
    tasks_processed += 1
    print("Task complete")
    
@app.route("/metrics", methods=["GET"])
def metrics():
    return jsonify({
        "tasks_processed": tasks_processed
    })

if __name__ == "__main__":
    app.run(port=5005, debug=True)