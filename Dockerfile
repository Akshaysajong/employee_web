# Use an official Python runtime as a parent image
# Python 3.11 is used for compatibility with latest package versions
FROM python:3.11

# Set environment variables for Python optimization
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# PYTHONUNBUFFERED: Ensures that Python output (stdout/stderr) is sent straight to terminal
# DJANGO_SETTINGS_MODULE: Tells Django which settings file to use
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=core.settings

# Set the working directory inside the container
# All subsequent commands will run from this directory
WORKDIR /app

# Install system dependencies required for Python packages and Nginx
# build-essential: Compiles Python packages with C extensions
# libpq-dev: PostgreSQL client library (required for psycopg2)
# nginx: Web server for reverse proxy and static file serving
# --no-install-recommends: Reduces image size by installing only essential packages
# rm -rf /var/lib/apt/lists/*: Cleans up apt cache to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    g++ \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# Copy requirements.txt first to leverage Docker layer caching
# --no-cache-dir: Reduces image size by not storing pip cache
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project source code
# This is done after installing dependencies to avoid rebuilding
# the entire image when only source code changes
COPY . .

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Make startup script executable
RUN chmod +x /app/start.sh

# Ensure we're in the correct working directory (redundant but explicit)
# This ensures the CMD runs from the correct directory
WORKDIR /app

# Expose the port that the Nginx will run on
# This allows external connections to the container
EXPOSE 80

# Default command to start both Django and Nginx
# The startup script will run both services
CMD ["/app/start.sh"]
