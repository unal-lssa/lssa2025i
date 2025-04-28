import os, textwrap, shutil


# Src: https://github.com/vishnubob/wait-for-it
# Used to wait for Kafka to be ready before starting the consumer/producer
def write_wait_for_it_script(destPath):
    os.makedirs(destPath, exist_ok=True)
    shutil.copy(
        os.path.join(os.getcwd(), "wait-for-it.sh"),
        os.path.join(destPath, "wait-for-it.sh"),
    )
    os.chmod(os.path.join(destPath, "wait-for-it.sh"), 0o755)  # Make it executable


def generate_consumer(name, target):
    path = f"skeleton/{name}"
    os.makedirs(path, exist_ok=True)

    app_code = textwrap.dedent(
        f"""
from flask import Flask
from kafka import KafkaConsumer
import os
import threading

app = Flask(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "{target}:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "upload-topic")
GROUP_ID = os.getenv("GROUP_ID", "saver-group")
SAVE_PATH = os.getenv("SAVE_PATH", "/tmp")

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id=GROUP_ID,
    auto_offset_reset="earliest",
)


def consume_loop():
    for message in consumer:
        filename = os.path.join(SAVE_PATH, "received_file " + str(message.offset))
        print(f"Saving file to " + filename)
        with open(filename, "wb") as f:
            f.write(message.value)


# Start consumer loop in a separate thread
threading.Thread(target=consume_loop, daemon=True).start()


@app.route("/health", methods=["GET"])
def health_check():
    return {{"status": "consumer running"}}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
"""
    )

    requirements = ["flask", "kafka-python"]

    with open(os.path.join(path, "app.py"), "w", encoding="utf8") as f:
        f.write(app_code)

    write_wait_for_it_script(path)

    with open(os.path.join(path, "Dockerfile"), "w", encoding="utf8") as f:
        requirements_str = "\n".join([f"RUN pip install {req}" for req in requirements])
        f.write(
            textwrap.dedent(
                f"""
FROM python:3.11-slim
WORKDIR /app
COPY . /app

RUN chmod +x /app/wait-for-it.sh

RUN apt-get update && apt-get install -y netcat-traditional
{requirements_str}

ENTRYPOINT ["/app/wait-for-it.sh", "{target}:9092", "--timeout=120", "--strict", "--", "python", "app.py"]
"""
            )
        )


def generate_producer(name, target):
    path = f"skeleton/{name}"
    os.makedirs(path, exist_ok=True)

    app_code = textwrap.dedent(
        f"""
from flask import Flask, request, jsonify
from kafka import KafkaProducer
import os

app = Flask(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "{target}:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "upload-topic")

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if file:
        producer.send(KAFKA_TOPIC, file.read())
        return jsonify({{"status": "file uploaded"}}), 200
    return jsonify({{"error": "No file provided"}}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    """
    )

    requirements = ["flask", "kafka-python"]

    with open(os.path.join(path, "app.py"), "w", encoding="utf8") as f:
        f.write(app_code)

    write_wait_for_it_script(path)

    with open(os.path.join(path, "Dockerfile"), "w", encoding="utf8") as f:
        requirements_str = "\n".join([f"RUN pip install {req}" for req in requirements])
        f.write(
            textwrap.dedent(
                f"""
FROM python:3.11-slim
WORKDIR /app
COPY . /app

RUN chmod +x /app/wait-for-it.sh

RUN apt-get update && apt-get install -y netcat-traditional
{requirements_str}

ENTRYPOINT ["/app/wait-for-it.sh", "{target}:9092", "--timeout=120", "--strict", "--", "python", "app.py"]
"""
            )
        )
