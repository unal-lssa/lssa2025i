FROM python:3.11-slim

WORKDIR /app

COPY /shared/auth_utils.py templates/shared/auth_utils.py

COPY /auth_be/app.py .

COPY /efact_ag/requirements.txt .

RUN pip install flask pyjwt requests python-dotenv -r requirements.txt

CMD ["python", "app.py"]