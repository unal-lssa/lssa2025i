FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install flask

EXPOSE 5002

CMD ["python", "database.py"] 