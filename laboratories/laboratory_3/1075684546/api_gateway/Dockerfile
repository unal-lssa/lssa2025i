FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api_gateway.py .

EXPOSE 5000

CMD ["python", "api_gateway.py"]