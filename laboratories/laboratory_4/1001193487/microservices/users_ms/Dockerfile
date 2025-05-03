FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir flask requests python-dotenv redis
CMD ["python", "-u", "users_ms.py"]