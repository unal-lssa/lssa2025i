# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir Flask==2.3.2 PyJWT==2.7.0 requests==2.31.0

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "api_gateway.py"]