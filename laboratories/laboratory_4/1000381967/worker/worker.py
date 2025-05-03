import pika
import time
import json

def process_task(body):
    print(f"Procesando tarea: {body}")
    time.sleep(30)  # Simulación de trabajo pesado
    print("Tarea completada")

def wait_for_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq-queue',
                    credentials=pika.PlainCredentials('user', 'password')
                )
            )
            print("✅ Conexión a RabbitMQ exitosa.")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("⏳ Esperando a que RabbitMQ esté disponible...")
            time.sleep(5)

def main():
    connection = wait_for_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue='tasks')

    def callback(ch, method, properties, body):
        task = json.loads(body)
        process_task(task)

    channel.basic_consume(queue='tasks', on_message_callback=callback, auto_ack=True)
    print(" [*] Esperando tareas en la cola. Presiona Ctrl+C para salir.")
    channel.start_consuming()

if __name__ == "__main__":
    main()
