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

def process_task(data):
    print(f"Processing task: {data}", flush=True)
    time.sleep(5) # Simulate delay
    print("Task complete", flush=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)