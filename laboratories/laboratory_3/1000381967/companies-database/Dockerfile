FROM python:3.9-alpine

RUN pip install --no-cache-dir \
    Flask==3.1.0 

COPY database.py .

CMD ["python", "database.py"]