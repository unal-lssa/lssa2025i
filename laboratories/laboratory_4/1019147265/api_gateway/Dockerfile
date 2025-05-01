# Dockerfile for API Gateway
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "api_gateway.py"]