FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir flask
CMD ["python", "users_db.py"]