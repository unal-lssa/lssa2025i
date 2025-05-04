from flask import Flask, jsonify
import uuid
import time

app = Flask(__name__)
instance_id = str(uuid.uuid4())[:8] # ID único

@app.route("/process", methods=["GET"])
def process():
    # Simular carga diferente según el servicio
    # Puerto 5001: carga baja, 5007: carga media, 5008: carga alta
    port = app.config.get('PORT', 5001)
    
    if port == 5001:
        processing_time = 0.2 # Más rápido
    elif port == 5007:
        processing_time = 0.5 # Medio
    else:
        processing_time = 1.0 # Más lento
    
    time.sleep(processing_time)
    
    return jsonify({
        'message': 'Business logic executed', 
        'instance': instance_id,
        'processing_time': processing_time
    }), 200

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app.config['PORT'] = port
    print(f"Microservicio iniciando en puerto {port} (Instance ID: {instance_id})")
    app.run(port=port, debug=True)