FROM python:3.11-slim

WORKDIR /app

COPY ./shared/auth_utils.py .

COPY ./data_service/data_service.py .

RUN pip install flask pyjwt requests python-dotenv

CMD ["python", "data_service.py"]