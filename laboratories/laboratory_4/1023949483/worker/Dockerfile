# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir Flask==2.3.2

# Expose the port the app runs on
EXPOSE 5005

# Command to run the application
CMD ["python", "worker.py"]