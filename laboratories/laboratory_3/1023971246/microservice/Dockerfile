FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install flask

EXPOSE 5001

CMD ["python", "microservice.py"]