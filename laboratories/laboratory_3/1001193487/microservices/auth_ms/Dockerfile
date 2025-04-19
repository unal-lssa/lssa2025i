FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir flask pyJWT requests python-dotenv
CMD ["python", "auth_ms.py"]