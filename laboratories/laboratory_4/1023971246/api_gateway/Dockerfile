FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install flask pyjwt requests

EXPOSE 5000

CMD ["python", "api_gateway.py"] 