FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir textX mysql-connector-python flask pyjwt requests

CMD ["python", "generation.py"]