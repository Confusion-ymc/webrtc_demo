# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv, a fast Python package installer
RUN pip install uv

# Copy project definition file
COPY pyproject.toml .

# Install dependencies from pyproject.toml
RUN uv pip install --no-cache-dir . --system

# Copy the rest of the application's code into the container
COPY . .

# Generate self-signed certificate for HTTPS
# Note: For production, you should use a proper certificate from a CA.
RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=YOUR_DOMAIN.COM"

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application
# Runs uvicorn with HTTPS enabled
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--ssl-keyfile", "./key.pem", "--ssl-certfile", "./cert.pem"]
