FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install flask

EXPOSE 8000

CMD ["python", "load_balancer.py"] 