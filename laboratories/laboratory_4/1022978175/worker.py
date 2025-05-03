from flask import Flask, request, jsonify
import threading
import time
import queue
import json
from datetime import datetime

app = Flask(__name__)

# Task queues with different priorities
task_queues = {
    "high": queue.PriorityQueue(),
    "normal": queue.PriorityQueue(),
    "low": queue.PriorityQueue()
}

# Track task statistics
stats = {
    "total_tasks": 0,
    "completed_tasks": 0,
    "failed_tasks": 0,
    "queue_lengths": {
        "high": 0,
        "normal": 0,
        "low": 0
    },
    "avg_processing_time": 0
}

# Configure worker threads
NUM_WORKERS = 3
worker_threads = []
shutdown_flag = False

def get_priority_value(priority_name):
    """Convert priority name to numeric value (lower = higher priority)"""
    if priority_name == "high":
        return 0
    elif priority_name == "low":
        return 2
    return 1  # Default "normal" priority

def worker_thread(worker_id):
    """Worker thread function that processes tasks from queues"""
    print(f"Worker {worker_id} started")
    
    total_processing_time = 0
    tasks_processed = 0
    
    while not shutdown_flag:
        task = None
        queue_checked = None
        
        # Check high priority queue first, then normal, then low
        for priority in ["high", "normal", "low"]:
            if not task_queues[priority].empty():
                try:
                    # Get task but maintain priority inside the queue
                    _, task = task_queues[priority].get(block=False)
                    queue_checked = priority
                    break
                except queue.Empty:
                    continue
        
        if task is None:
            # No tasks in any queue, sleep briefly
            time.sleep(0.1)
            continue
        
        # Process the task
        print(f"Worker {worker_id} processing task from {queue_checked} queue: {task}")
        
        try:
            start_time = time.time()
            
            # Extract task parameters
            task_type = task.get("task_type", "default")
            duration = task.get("duration", 5)  # Default 5 second task
            should_fail = task.get("fail", False)
            
            if should_fail:
                print(f"Worker {worker_id}: Task {task} simulating failure")
                raise Exception("Simulated task failure")
            
            # Simulate different processing based on task type
            if task_type == "cpu_intensive":
                # Simulate CPU-heavy work
                result = 0
                for i in range(1000000):
                    result += i
                print(f"Worker {worker_id}: CPU-intensive result: {result}")
                time.sleep(duration * 0.5)  # Still sleep, but less
                
            elif task_type == "io_intensive":
                # Simulate I/O waiting
                print(f"Worker {worker_id}: Simulating I/O operations")
                time.sleep(duration * 1.5)  # Sleep longer to simulate I/O
                
            else:
                # Default processing
                print(f"Worker {worker_id}: Processing default task")
                time.sleep(duration)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update stats
            with stats_lock:
                stats["completed_tasks"] += 1
                stats["queue_lengths"][queue_checked] -= 1
                
                # Update average processing time
                total_processing_time += processing_time
                tasks_processed += 1
                stats["avg_processing_time"] = total_processing_time / tasks_processed
            
            print(f"Worker {worker_id} completed task in {processing_time:.2f}s")
            
        except Exception as e:
            print(f"Worker {worker_id} encountered error: {str(e)}")
            with stats_lock:
                stats["failed_tasks"] += 1
                stats["queue_lengths"][queue_checked] -= 1
        
        finally:
            # Mark task as done in the queue
            task_queues[queue_checked].task_done()

# Thread to monitor queues and stats
def monitor_thread():
    """Periodically logs queue stats"""
    while not shutdown_flag:
        with stats_lock:
            high_tasks = task_queues["high"].qsize()
            normal_tasks = task_queues["normal"].qsize()
            low_tasks = task_queues["low"].qsize()
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Queue status - " +
                  f"High: {high_tasks}, Normal: {normal_tasks}, Low: {low_tasks}")
            print(f"Tasks - Total: {stats['total_tasks']}, " +
                  f"Completed: {stats['completed_tasks']}, Failed: {stats['failed_tasks']}")
        
        time.sleep(5)  # Report every 5 seconds

# Lock for thread-safe updates to stats
stats_lock = threading.Lock()

@app.route("/task", methods=["POST"])
def handle_task():
    data = request.json
    
    # Determine priority (default to normal)
    priority_name = data.pop("_meta", {}).get("priority", "normal")
    if priority_name not in ["high", "normal", "low"]:
        priority_name = "normal"
    
    # Add timestamp
    data["_timestamp"] = time.time()
    
    # Calculate priority value (lower number = higher priority)
    priority_value = get_priority_value(priority_name)
    
    # Add to appropriate queue with priority value
    task_queues[priority_name].put((priority_value, data))
    
    # Update stats
    with stats_lock:
        stats["total_tasks"] += 1
        stats["queue_lengths"][priority_name] += 1
    
    return jsonify({
        "status": "Task queued",
        "queue": priority_name,
        "position": task_queues[priority_name].qsize()
    }), 202

@app.route("/stats", methods=["GET"])
def get_stats():
    with stats_lock:
        current_stats = stats.copy()
        # Add current queue sizes
        current_stats["current_queue_sizes"] = {
            "high": task_queues["high"].qsize(),
            "normal": task_queues["normal"].qsize(),
            "low": task_queues["low"].qsize()
        }
    return jsonify(current_stats)

def start_worker_threads():
    """Start all worker threads"""
    global worker_threads
    
    for i in range(NUM_WORKERS):
        thread = threading.Thread(target=worker_thread, args=(i,), daemon=True)
        thread.start()
        worker_threads.append(thread)
    
    # Start monitor thread
    monitor = threading.Thread(target=monitor_thread, daemon=True)
    monitor.start()
    worker_threads.append(monitor)

if __name__ == "__main__":
    # Start worker threads before the Flask app
    start_worker_threads()
    app.run(port=5005, debug=False)  # Use debug=False with threads
