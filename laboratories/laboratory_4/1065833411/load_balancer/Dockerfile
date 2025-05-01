FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY load_balancer.py .
CMD ["python", "load_balancer.py"]