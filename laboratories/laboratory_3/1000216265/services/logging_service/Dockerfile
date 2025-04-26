FROM python:3.9-slim

WORKDIR /app

COPY app.py .

RUN pip install --no-cache-dir flask

VOLUME ["/app/logs"]

EXPOSE 5004

CMD ["python", "app.py"]
