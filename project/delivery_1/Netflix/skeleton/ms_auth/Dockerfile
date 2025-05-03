FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask 
EXPOSE 8003
CMD ["python", "app.py"]