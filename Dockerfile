# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Install system dependencies required for the application
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    wireguard-tools \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the Python dependencies file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python dependencies file and install them
COPY app/ ./app/

# Define a persistent volume for storing database and configuration files
VOLUME ["/data"]

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Define the default command to run the FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
