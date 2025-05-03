# Dockerfile for Login Service
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install flask pyjwt
CMD ["python", "login_service.py"]