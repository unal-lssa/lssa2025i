FROM python:3.9-alpine

WORKDIR /app

RUN pip install --no-cache-dir \
    Flask==3.1.0 \
    PyJWT==2.10.1 

COPY database.py .

CMD ["python", "database.py"]     