FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir textX mysql-connector-python flask

COPY . .

CMD ["python", "generation.py"]
