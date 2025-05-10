FROM python:3.11-slim

WORKDIR /app

COPY ./shared/auth_utils.py .
COPY db_service/database.py .

RUN pip install flask pyjwt requests python-dotenv

CMD ["python", "database.py"]