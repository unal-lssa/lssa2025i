FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install flask pyjwt requests python-dotenv

CMD ["python", "app.py"]