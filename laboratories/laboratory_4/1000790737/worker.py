from flask import Flask, request, jsonify
import threading, time
import requests

app = Flask(__name__)
CACHE_URL = "http://worker_cache:5010/cache/task_results"


@app.route("/task", methods=["POST"])
def handle_task():
    data = request.json
    thread = threading.Thread(target=process_task, args=(data,))
    thread.start()
    return jsonify({"status": "Started"}), 202


def process_task(data):
    print(f"Processing task: {data}")
    time.sleep(5)
    result = f"Result for {data}"
    requests.post(CACHE_URL, json={"value": result})
    print("Task complete")


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5008
    app.run(host="0.0.0.0", port=port, debug=True)
