from flask import Flask, request, jsonify
import threading
import time
from utils.logger import setup_logger

# Configurar el logger
logger = setup_logger("Worker", "worker.log")

app = Flask(__name__)

@app.route("/task", methods=["POST"])
def handle_task():
    data = request.json
    thread = threading.Thread(target=process_task, args=(data,))
    thread.start()
    return jsonify({'status': 'Started'}), 202

def process_task(data):
    print(f"Processing task: {data}")
    time.sleep(5)  # Simulate delay
    print("Task complete")

if __name__ == "__main__":
     app.run(host="0.0.0.0",port=5005, debug=True)