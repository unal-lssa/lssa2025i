FROM python:3.11-slim

WORKDIR /app

COPY ./shared/auth_utils.py .
COPY microservice/microservice.py .

RUN pip install flask pyjwt requests python-dotenv

CMD ["python", "microservice.py"]