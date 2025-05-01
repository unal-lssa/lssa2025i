# Dockerfile for Load Balancer
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "load_balancer.py"]