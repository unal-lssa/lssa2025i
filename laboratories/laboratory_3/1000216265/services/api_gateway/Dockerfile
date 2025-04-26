FROM python:3.9-slim

WORKDIR /app

COPY app.py .

RUN pip install --no-cache-dir flask requests pyjwt

EXPOSE 5000

CMD ["python", "app.py"]
