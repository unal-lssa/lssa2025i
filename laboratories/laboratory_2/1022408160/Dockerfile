FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir textx mysql-connector-python flask

CMD ["python", "generation.py"]
