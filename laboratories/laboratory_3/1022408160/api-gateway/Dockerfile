# Dockerfile.gateway

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the specific requirements file for the gateway
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the gateway python file into the container at /app
COPY app.py .

# Make the gateway port available
EXPOSE 5050

# Run gateway.py when the container launches
CMD ["python", "app.py"]