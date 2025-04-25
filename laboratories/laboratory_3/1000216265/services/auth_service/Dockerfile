FROM python:3.9-slim

WORKDIR /app

COPY app.py .

RUN pip install --no-cache-dir flask pyjwt bcrypt

EXPOSE 5001

CMD ["python", "app.py"]
