FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install flask

EXPOSE 5004

CMD ["python", "cache.py"] 