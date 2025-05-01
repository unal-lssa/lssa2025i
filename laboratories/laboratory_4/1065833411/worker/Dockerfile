FROM python:3.9
WORKDIR /app
COPY worker.py .
RUN pip install flask
CMD ["python", "worker.py"]