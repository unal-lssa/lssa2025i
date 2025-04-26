# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required Python packages directly
RUN pip install --no-cache-dir Flask==2.2.3 PyJWT==2.6.0 Werkzeug==2.2.3

# Expose the port the app runs on
EXPOSE 5003

# Define environment variable
ENV FLASK_APP=clients_ms.py

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5003"]