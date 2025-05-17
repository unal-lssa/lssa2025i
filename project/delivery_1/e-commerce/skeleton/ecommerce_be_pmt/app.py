
from flask import Flask, request, jsonify
import mysql.connector
import pika
import threading
import json
import time

app = Flask(__name__)

# Setup RabbitMQ connection
def setup_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            channel.queue_declare(queue='payments', durable=True)
            return connection, channel
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            time.sleep(5)

def start_consumer():
    connection, channel = setup_rabbitmq()

    def callback(ch, method, properties, body):
        payment_data = json.loads(body)
        process_payment(payment_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='payments', on_message_callback=callback)
    print('Payment service started consuming')
    try:
        channel.start_consuming()
    except Exception as e:
        print(f"Consumer error: {e}")
        connection.close()
        time.sleep(5)
        start_consumer()

def process_payment(payment_data):
    conn = mysql.connector.connect(
        host='None',
        user='root',
        password='root',
        database='None'
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (order_id, amount, status) VALUES (%s, %s, %s)", 
                  (payment_data['order_id'], payment_data['amount'], 'processed'))
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/process', methods=['POST'])
def queue_payment():
    data = request.json
    connection, channel = setup_rabbitmq()
    channel.basic_publish(
        exchange='',
        routing_key='payments',
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    connection.close()
    return jsonify(status="payment queued")

@app.route('/health')
def health():
    return jsonify(status="ok")

if __name__ == '__main__':
    # Start consumer in a separate thread
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()

    # Start the Flask app
    app.run(host='0.0.0.0', port=80)
