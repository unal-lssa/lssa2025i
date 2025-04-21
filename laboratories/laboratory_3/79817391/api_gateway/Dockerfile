FROM python:3.11-slim

WORKDIR /app

COPY ./shared/auth_utils.py .

COPY ./api_gateway/api_gateway.py .

RUN pip install flask pyjwt requests python-dotenv

CMD ["python", "api_gateway.py"]