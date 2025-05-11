FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The command to run the worker is in docker-compose.yml
CMD ["tail", "-f", "/dev/null"] # Keep container running while docker-compose starts worker command