from flask import Flask, request, jsonify
import threading
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/task", methods=["POST"])
def handle_task():
    data = request.json
    logger.info(f"Received task with data: {data}")
    thread = threading.Thread(target=process_task, args=(data,))
    thread.start()
    return jsonify({'status': 'Started'}), 202

def process_task(data):
    logger.info(f"Starting to process task: {data}")
    time.sleep(10)  # Simulate delay
    logger.info("Task processing complete")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5005, debug=True)