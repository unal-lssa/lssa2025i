
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size, --upgrade ensures latest pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
# This assumes your app.py is in the same directory as this Dockerfile
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable (optional, can be overridden in docker-compose)
# ENV FLASK_APP=app.py # Not strictly needed if using CMD below
ENV FLASK_RUN_HOST=0.0.0.0

# Run app.py when the container launches
# Use python directly instead of flask run for better control in some environments
CMD ["python", "app.py"]