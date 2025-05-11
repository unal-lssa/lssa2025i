FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir flask requests python-dotenv Flask-Limiter
EXPOSE 5000
CMD ["python", "api_gateway.py"]