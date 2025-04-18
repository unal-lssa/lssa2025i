FROM python:3.9-alpine

WORKDIR /app

RUN pip install --no-cache-dir \ 
    Flask==3.1.0 \
    requests==2.32.3

COPY microservice.py .

CMD ["python", "microservice.py"]