FROM python:3.11-slim

WORKDIR /app

COPY /shared/auth_utils.py templates/shared/auth_utils.py

COPY /efact_ag/api_gateway.py .

COPY /efact_ag/requirements.txt .

RUN pip install flask pyjwt requests python-dotenv -r requirements.txt

CMD ["python", "api_gateway.py"]