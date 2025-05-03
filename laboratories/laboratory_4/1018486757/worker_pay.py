from flask import Flask, request, jsonify 
import threading 
import time 
app = Flask(__name__) 

@app.route("/microservice_pay", methods=["POST"])

def handle_task(): 
    data = request.json 
    thread = threading.Thread(target=process_task, args=(data,)) 
    thread.start() 
    return jsonify({'status': 'Started'}), 202

def process_task(data): 
    print(f"Processing task pay: {data}") 
    time.sleep(5)  # Simulate delay 
    print("Task complete") 

if __name__ == "__main__": 
    app.run(port=5008, debug=True) 